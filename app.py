import flask
import db
import local_types
import os
from analyze_attributions import analyze_attributions, save_analysis_results

app = flask.Flask("Spidiagmir_App", template_folder="templates", static_folder="static")

def get_database():
    database = getattr(flask.g, "_database", None)
    if database is None:
        database = flask.g._database = db.Database(os.path.join(app.root_path, "spidiagmir_export.db"))

    return database

@app.teardown_appcontext
def close_database(exception):
    database = getattr(flask.g, "_database", None)
    if database is not None:
        del database

@app.route("/")
def root():
    return flask.redirect("/index")

@app.route("/index")
def index():
    return flask.render_template("index.html")

@app.route("/search")
def search():
    try:
        database = get_database()
        query = flask.request.args.get("query")
        query = local_types.SpectralQuery(flask.request.args)
        database.spectral_search(query)
        print("-"*50)
    except ValueError as e:
        return flask.render_template("error.html", error=str(e))
    return flask.render_template("search_result.html")

@app.route("/article/<int:pmcid>")
def article(pmcid):
    try:
        database = get_database()
        article = database.get_full_article_info(pmcid)
    except ValueError as e:
        return flask.render_template("error.html", error=str(e))
    return flask.render_template("article.html", article=article)

@app.route("/api/spectral-search")
def api_search():
    try:
        database = get_database()
        query = local_types.SpectralQuery(flask.request.args)
        results = database.spectral_search(query)
        return results
    except Exception as e:
        print(e)
        return flask.jsonify({"error": str(e)}), 400
    
@app.route("/api/article-search")
def api_article_search():
    try:
        database = get_database()
        query = local_types.ArticleQuery(flask.request.args)
        results = database.article_search(query)
        return results
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 400

@app.route("/save_csv", methods=["POST"])
def save_csv():
    content = flask.request.json
    csv_data = content['csv']
    csv_file_path = os.path.join('SPIDIAGMIR_APP', 'tables', 'bands_data.csv')
    with open(csv_file_path, 'w', encoding='utf-8') as f:
        f.write(csv_data)
    return flask.jsonify({"message": "CSV file saved successfully."}), 200

@app.route("/analyse")
def analyse():
    return flask.render_template("analyse.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in flask.request.files:
        return flask.redirect(flask.url_for('analyse'))
    
    file = flask.request.files['file']
    if file.filename == '':
        return flask.redirect(flask.url_for('analyse'))

    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        bond_counter = analyze_attributions(file_path)
        output_file = os.path.join('uploads', 'chemical_entities_analysis.csv')
        save_analysis_results(bond_counter, output_file)
        return flask.render_template("analyse.html", analysis=bond_counter)

@app.route("/download_csv")
def download_csv():
    return flask.send_file("uploads/chemical_entities_analysis.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=False)