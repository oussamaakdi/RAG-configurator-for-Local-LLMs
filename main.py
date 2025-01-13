from Rag import Configuration
from flask import Flask, render_template, request, jsonify
from flask import flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import numpy as np


global_configurations = dict()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'votre_cle_secrete'  

db = SQLAlchemy(app)





class RAGConfiguration(db.Model):
    __tablename__ = 'configurations'

    id = db.Column(db.Integer, primary_key=True)  
    config_name = db.Column(db.String(100), nullable=False)  
    rem = db.Column(db.String(100), nullable=False)  
    top_k = db.Column(db.Integer, nullable=False) 
    approach = db.Column(db.String(50), nullable=False) 
    llm = db.Column(db.String(100), nullable=False)  
    eem = db.Column(db.String(100), nullable=False)  
    similarity_threshold = db.Column(db.Float, nullable=False)  
    answer_relevancy = db.Column(db.Float, nullable=True)  
    context_precision = db.Column(db.Float, nullable=True) 
    faithfulness = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'config_name': self.config_name,
            'rem': self.rem,
            'top_k': self.top_k,
            'approach': self.approach,
            'llm': self.llm,
            'eem': self.eem,
            'similarity_threshold': self.similarity_threshold,
            'metrics': {
                'Answer_Relevancy': self.answer_relevancy,
                'Context_Precision': self.context_precision,
                'Faithfulness': self.faithfulness,
            }
        }
#--------------------------------------
@app.route('/')
def index():
    return render_template('home.html')
#--------------------------------------
@app.route('/configs', methods=['GET'])
def get_all_configs():
    configs = RAGConfiguration.query.all()
    return render_template('history.html', configs=configs)
#--------------------------------------
@app.route('/configs/<int:config_id>', methods=['POST', 'DELETE'])
def delete_config(config_id):
    if request.method == 'POST' and request.form.get('_method') != 'DELETE':
        return jsonify({"error": "Invalid method override"}), 405

    config = RAGConfiguration.query.get(config_id)
    if not config:
        return jsonify({"error": "Configuration introuvable"}), 404

    db.session.delete(config)
    db.session.commit()
    return redirect(url_for('get_all_configs'))
#----------------------------------------
@app.route('/configs/form', methods=['GET'])
def show_config_form():
    return render_template('configurations.html')
#----------------------------------------
@app.route('/configs/add', methods=['POST'])
def add_config_form():
    try:
        print("Données reçues :", request.form)
        config_name = request.form.get('config_name', '').strip()
        rem = request.form.get('rem', '').strip()
        top_k = request.form.get('top_k')
        approach = request.form.get('approach', '').strip()
        llm = request.form.get('llm', '').strip()
        eem = request.form.get('eem', '').strip()
        similarity_threshold = request.form.get('similarity_threshold')

        if not config_name or not rem or not top_k or not approach or not llm or not eem or not similarity_threshold:
            raise ValueError("Tous les champs obligatoires doivent être remplis.")

        top_k = int(top_k)
        similarity_threshold = float(similarity_threshold)

        new_config = RAGConfiguration(
            config_name=config_name,
            rem=rem,
            top_k=top_k,
            approach=approach,
            llm=llm,
            eem=eem,
            similarity_threshold=similarity_threshold,
            answer_relevancy=None,  
            context_precision=None,  
            faithfulness=None  
        )
        db.session.add(new_config)
        db.session.commit()

        flash(f"Configuration '{config_name}' ajoutée avec succès !", "success")

        return redirect(url_for('get_all_configs'))

    except ValueError as ve:
        flash(f"Erreur : {str(ve)}", "danger")
        return redirect(url_for('show_config_form'))
    except Exception as e:
        flash(f"Erreur inattendue : {str(e)}", "danger")
        return redirect(url_for('show_config_form'))
#----------------------------------------------------
@app.route('/configs/update_metrics/<string:config_name>/<float:answer_relevancy>/<float:context_precision>/<float:faithfulness>', methods=['POST','GET'])
def update_metrics(config_name, answer_relevancy, context_precision, faithfulness):
    try:
        config = RAGConfiguration.query.filter_by(config_name=config_name).first()
        if not config:
            return jsonify({"error": "Configuration introuvable"}), 404

        config.answer_relevancy = round(answer_relevancy,3)
        config.context_precision = round(context_precision,3)
        config.faithfulness = round(faithfulness,3)
        db.session.commit()
        flash(f"Métriques mises à jour pour la configuration '{config_name}'")
        return redirect(url_for('get_all_configs'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#---------------------------------------------------

@app.route('/configs/evaluate/<int:config_id>', methods=['POST', 'GET'])
def evaluate_config(config_id):
    try:
        config = RAGConfiguration.query.get(config_id)
        if not config:
            return jsonify({"error": "Configuration introuvable"}), 404

        upload = Configuration(
            config_name=config.config_name,
            rem=config.rem,
            top_k=config.top_k,
            approach=config.approach,
            llm=config.llm,
            eem=config.eem,
            similarity_threshold=config.similarity_threshold
        )
        upload.fit()

        metr = upload.measures()

        ar = round(metr['Answer_Relevancy'],3)
        cp = round(metr['Context_Precision'],3)
        fa = round(metr['Faithfulness'],3)

        return redirect(url_for(
            'update_metrics',
            config_name=config.config_name,
            answer_relevancy=ar,
            context_precision=cp,
            faithfulness=fa
        ))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#----------------------------------------------------

@app.route('/chatbot/choose')
def let_choose():
    configs = RAGConfiguration.query.all()
    return render_template('selection.html', configs= configs)
#---------------------------------------------------
@app.route('/chatbot/select', methods=['POST'])
def select_chatbot_config():
    config_id = request.form.get('config_id')
    config = db.session.get(RAGConfiguration, config_id)

    if not config:
        return jsonify({"error": "Configuration introuvable"}), 404

    if config_id in global_configurations:
        return redirect(url_for('chatbot_discussion', config_id=config_id))

    chat_instance = Configuration(
        config_name=config.config_name,
        rem=config.rem,
        top_k=config.top_k,
        approach=config.approach,
        llm=config.llm,
        eem=config.eem,
        similarity_threshold=config.similarity_threshold
    )
    chat_instance.fit()

    global_configurations[str(config_id)] = chat_instance
    return redirect(url_for('chatbot_discussion', config_id=config_id))
#--------------------------------------------------------

@app.route('/chatbot/directe/discussion/<int:config_id>', methods=['GET'])
def chatbot_directe_discussion(config_id):
    config = RAGConfiguration.query.get(config_id)
    if not config:
        return jsonify({"error": "Configuration introuvable"}), 404

    chat_instance = global_configurations.get(str(config_id))
    if not chat_instance:
        chat_instance = Configuration(
            config_name=config.config_name,
            rem=config.rem,
            top_k=config.top_k,
            approach=config.approach,
            llm=config.llm,
            eem=config.eem,
            similarity_threshold=config.similarity_threshold
        )
        chat_instance.fit()
        global_configurations[str(config_id)] = chat_instance

    return render_template("discussion.html", config_id=config_id)

#----------------------------------------------------
@app.route('/chatbot/discussion/<int:config_id>', methods=['GET'])
def chatbot_discussion(config_id):
    return render_template('discussion.html', config_id=config_id)

#----------------------------------------------------
@app.route('/chatbot/ask/<int:config_id>', methods=['POST'])
def chatbot_ask(config_id):
    data = request.get_json()
    query = data.get('query')

    chat_instance = global_configurations.get(str(config_id))

    if not chat_instance:
        return jsonify({"error": "Configuration introuvable"}), 404

    response = chat_instance.predict(query)
    print(f"Response sent: {response}")

    return jsonify({"response": response})






if __name__ == '__main__':
   app.run(debug=True)
