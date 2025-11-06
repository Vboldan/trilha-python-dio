# Lembre-se de alterar o caminho do arquivo, para o caminho completo da sua máquina!

arquivo = open(
    "/home/valdeci/Área de trabalho/Teste.txt", "r"
)
print(arquivo.read())
arquivo.close()

arquivo = open(
    "/home/valdeci/Área de trabalho/Teste.txt", "r"
)
print(arquivo.readline())
arquivo.close()

arquivo = open(
    "/home/valdeci/Área de trabalho/Teste.txt", "r"
)
print(arquivo.readlines())
arquivo.close()

arquivo = open(
    "/home/valdeci/Área de trabalho/Teste.txt", "r"
)
# tip
while len(linha := arquivo.readline()):
    print(linha)

arquivo.close()
