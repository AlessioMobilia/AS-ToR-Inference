def leggi_file(nome_file):
    ases = []
    with open(nome_file, 'r') as file:
        for line in file:
            line = line.strip()
            tupla = [None,None]
            tupla[0] = line.split('|')[0]
            tupla[1] = line.split('|')[1]
            ases.append(tupla)
        return ases

def rimuovi_duplicati(file_peer, file_up,file_finale):
    peers = leggi_file(file_peer)
    ups = leggi_file(file_up)

    for ases in peers:
        found= False
        if(ases in ups):
            found = True
        if([ases[1],ases[0]] in ups):
            found = True
        if(not found):
            with open(file_finale, 'a') as file:
                file.write(f"{ases[0]}|{ases[1]}|0\n")

    for ases in ups:
        found= False
        if(ases in peers):
            found = True
        if([ases[1],ases[0]] in peers):
            found = True
        if(not found):
            with open(file_finale, 'a') as file:
                file.write(f"{ases[0]}|{ases[1]}|1\n")


    return

if __name__ == "__main__":
    file_peer = "peer.csv"
    file_up = "upstream.csv"
    file_finale = "file_finale.txt"

    rimuovi_duplicati(file_peer, file_up, file_finale)

    print(f"I dati sono stati scritti nel file {file_finale}")
