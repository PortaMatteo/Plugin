# pip install python-dotenv
import os
import openai
from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        text = request.form["input"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            max_tokens=30,
            temperature=0,
        )
        print(response)
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)
