from flask import Flask, request, render_template_string

app = Flask(__name__)

FORM = """
<!doctype html>
<html>
  <body>
    <h1>SSTI GET Method Test</h1>
    <form>
      <input name="name" placeholder="예: junwon"/>
      <button>확인</button>
    </form>
  </body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    name = request.args.get('name')
    if not name:
        return render_template_string(FORM)

    tpl = f"""
    <!doctype html>
    <html>
      <body>
      <h2>Hello! { name }</h2>
        <p><a href="/">다시</a></p>
      </body>
    </html>
    """
    return render_template_string(tpl, name=name)

if __name__ == '__main__':
    app.run(debug=True)
