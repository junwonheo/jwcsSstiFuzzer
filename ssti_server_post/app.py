from flask import Flask, request, render_template_string

app = Flask(__name__)

FORM = """
<!doctype html>
<html>
  <body>
    <h1>SSTI POST Method Test</h1>
    <form action="/" method="POST">
      <input name="name" placeholder="예: junwon"/>
      <button>확인</button>
    </form>
  </body>
</html>
"""

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template_string(FORM)

    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            return render_template_string(FORM)
        tpl = f"""
        <!doctype html>
        <html>
        <body>
        <h2>Hello! Cookie: <script>document.write(document.cookie)</script><br>
        { name }</h2>
            <p><a href="/">다시</a></p>
        </body>
        </html>
        """
        return render_template_string(tpl, name=name)

if __name__ == '__main__':
    app.run(debug=True)
