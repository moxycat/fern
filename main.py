from fern import Fern

fern = Fern()

while True:
    text = input()
    print(fern.to_html(text))