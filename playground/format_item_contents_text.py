lines = '''#1  1   Tin square mini tote Glossy black
        Shirring mary jane shoes Ivory
        Classic tomboy shirt Pale blue stripe
    2   Mini around hobo bag Brownie brown
        Shirring mary jane shoes Ivory
        Classic tomboy shirt Pale blue stripe
    3   Mini root nylon backpack Black
        Soffy penny loafer Suede Black
        Classic tomboy shirt Pale blue stripe
    4   Tin square tote bag Glossy brownie brown
        Soffy penny loafer Suede Black
        Classic tomboy shirt Pale blue stripe
#2  1   Taco shoulder bag Brownie brown
        Shirring mary jane shoes Black
        Classic tomboy shirt Creamy corn
    2   Bud crossbody bag Black
        Shirring mary jane shoes Black
        Classic tomboy shirt Creamy corn
    3   Mini around hobo bag Creamy salmon
        Rowie mary jane shoes Charlie brown
        Classic tomboy shirt Creamy corn
    4   Pulpy hobo bag Cinnamon brown
        Rowie mary jane shoes Charlie brown
        Classic tomboy shirt Creamy corn
#3  1   Pebble medium shoulder bag Wrinkled black
        Dall platform mary jane shoes Black
    2   Pulpy hobo bag Black
        Dall platform mary jane shoes Black
    3   Curly tote bag Boucle Permanent mint
        Dall platform mary jane shoes Black
        Rohbit Gray
    4   Mini kiki messenger bag Wrinkled black
        Dall platform mary jane shoes Black
#4  1   Aline large shoulder bag Black
        Danghye mary jane shoes Charlie brown
    2   Cargo shouder bag Ivory
        Danghye mary jane shoes Charlie brown
    3   Root nylon backpack Black
        Danghye mary jane shoes Charlie brown
    4   Mini kiki messenger bag Wrinkled brownie brown
        Danghye mary jane shoes Charlie brown
#5  1   Tin square mini tote bag Glossy brownie brown
        Danghye mary jane shoes Black
    2   Around hobo bag Brownie brown
        Danghye mary jane shoes Black
    3   Mini root nylon backpack Misty blue
        Danghye mary jane shoes Black
    4   Pulpy hobo bag Nylon black
        Danghye mary jane shoes Black
#6  1   Mini pulpy hobo bag Black
        Rowie mary jane shoes Black
    2   Mini pulpy hobo bag Nylon ivory
        Rowie mary jane shoes Black
    3   Mono crossbody bag Creamy salmon
        Rowie mary jane shoes Black
    4   Rowie shoulder bag Leather Black
        Rowie mary jane shoes Black
#7  1   Pulpy hobo bag Nylon Umber
        Dall platform mary jane shoes Umber
    2   Cargo shouder bag Black
        Dall platform mary jane shoes Umber
    3   Mini pulpy hobo bag Nylon black
        Dall platform mary jane shoes Umber
#8  1   Mono crossbody bag Ivory
        Shirring mary jane shoes Ivory
    2   Curly tote bag Creamy salmon
        Shirring mary jane shoes Ivory
    3   Block tote bag Black
        Shirring mary jane shoes Ivory'''.split('\n')

series, sub_series, p = '', '', ''
texts = []
f = r'<p><a href=\"\/products\/block-tote-bag-black\" title=\"{name}\">{name}<\/a><\/p>'
for line in lines:
    parts = line.strip().split('   ')
    if len(parts) == 2:
        if p:
            texts.append(f'{p}",')
        if len(parts[0]) == 5:
            series, sub_series = list(map(str.strip, parts[0].split('  ')))
            print(series, sub_series)
        else:
            sub_series = parts[0]
            print(series, sub_series)
        current_series = f'{series}-{sub_series}'
        print(current_series)
        p = f'{current_series}:\n"content": "{f.format(name=parts[1].strip())}'
    else:
        p += f.format(name=parts[0].strip())
texts.append(f'{p}",')
for text in texts:
    print(text)

with open('contents.txt', 'w') as outf:
    for text in texts:
        outf.write(f'{text}\n')
