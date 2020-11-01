''' 	Copyright @ Hércules Mendes
		
		CLASSE QUE POSSIBILITA CRIARMOS UM ARRAY QUE AMARZENA UNSIGNED BYTES
		ESSA CLASSE PODE SER USADA PARA CRIAR QUALQUER TIPO DE OBJETO QUE 
		PRECISA LER E ESCREVER DADOS HEX EM UM DETERMINDO LOCAL DA MEMORIA (COMO POR EXEMPLO MEMORIA RAM 
		E REGISTRADORES).


		NO CASO DA MEMORIA RAM ELA TEM QUE ARMAZENA BYTES EM LOCAIS ESPECIFICOS DA MEMORIA QUE SAO 
		OS INDEX. A MEMORIA RAM ARMAZENA DADOS EM (HEX / LOCAL ) E LER DADOS EM (HEX / INSTRUÇÕES) 
'''

class UnsignedBitsArray:
	def __init__(self, cellLength, cellNumber):
		#ARMAZENA OS VALORES ABSOLUTOS DO TAMANHO(BYTE) E QUANTIDADE(IDEX) DE CELULAS
		self._cellLength = abs(cellLength) 
		self._cellNumber = abs(cellNumber)

		#CRIA UMA TABELA DE INTEIROS SEM SINAL.(CRIA O TAMANHO DA MEMORIA VAZIA)
		self._arr = [0] * self._cellNumber


	#RETORNA A TABELA DE IDEX E SEUS REPCTIVOS VALORES (EXIBIR NO DEBUGGER)
	def __str__(self):
		self.result = ''
		for idx, val in enumerate(self._arr):
			self.result += '{} : {}\n'.format(hex(idx), hex(val))
		return self.result


	#RETORNA O VALOR (INSTRUÇÃO DA MEMORIA) EM DETERMINADO IDEX (AÇÃO DE LEITURA DA MEMORIA RAM)
	def __getitem__(self, idx):
		return self._arr[idx]


	#DETERMINA O VALOR (INTRUÇÃO NA MEMORIA) EM DETERMINADO INDEX (AÇÃO DE ESCRITA MEMORIA RAM)
	#Ao definir um valor, ele permanece dentro dos limites de um inteiro sem sinal de bits de 
	#comprimento de célula. Se transbordar, apenas truncaremos os bits mais significativos para
	# reduzir o comprimento para cellLength. O módulo faz isso bem.
	def __setitem__(self, idx, value):
		self._arr[idx] = value % (2**self._cellLength)