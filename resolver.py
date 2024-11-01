from flask import Flask, redirect, abort, jsonify, render_template, g, request
from ark import ArkIdentifier, ArkFormatError
from mappers import IdMapper, JSONFileMapper, MetadataFormat, ResolveError

app = Flask(__name__)
naan = "77298"


@app.before_request
def before_request():
    # Můžeme zde inicializovat nebo nastavit jakékoli proměnné, které by mohly být potřeba
    g.error_message = 'Unspecified error.'


@app.errorhandler(404)
def page_not_found(e):
    # Proměnný text může být například uživatelsky definovaný popis chyby
    message = getattr(g, 'error_message', 'Invalid identifier')
    return render_template('404.html', message=message), 404


@app.errorhandler(400)
def page_not_found(e):
    # Proměnný text může být například uživatelsky definovaný popis chyby
    message = getattr(g, 'error_message', 'Invalid identifier')
    return render_template('400.html', message=message), 400


@app.errorhandler(500)
def page_not_found(e):
    message = getattr(g, 'error_message', 'Internal error')
    return render_template('500.html', message=message), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handle_path(path: str):
    IdMapper.loader([
        lambda: JSONFileMapper("", naan, "example0"),
    ], app.logger)
    try:
        # app.logger.debug(request.environ.get("RAW_URI"))
        ark = ArkIdentifier.parse(path)
        mapper = IdMapper.get_mapper_for_ark(ark)
        if request.environ.get("RAW_URI").endswith("?"):
            return jsonify(mapper.get_metadata(ark, MetadataFormat.Rdf_Json))
        else:
            return redirect(mapper.get_url(ark), code=301)
    except ResolveError as e:
        g.error_message = str(e)
        abort(404)
    except ArkFormatError as e:
        g.error_message = str(e)
        abort(400)
    except Exception as e:
        g.error_message = str(e)
        abort(500)


if __name__ == '__main__':
    app.run(debug=True)

