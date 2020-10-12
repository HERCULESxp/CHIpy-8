from unsignedbitsarray import UnsignedBitsArray


class RamMemory:
	def  __init__(self):
		self.memory = UnsignedBitsArray(8, 4096) #CRIA A MEMORIA RAM COM 4096 BYTES E VAZIA

	def WriteValue(self, idx, value):#ESCREVE  DADOS NA MEMORIA 
		self.memory[idx] = value

	def ReadValue(self, idx):#LER DADOS NA MEMORIA
		return self.memory[idx]

	def ClearRam():#ESVAZIA A MEMORIA
		for idx in self.memory:
			self.memory[idx] = 0
		pass

	def ShowValues(self):#MOSTRA OS VALORE DA MEMORIA (PARA DEBUG)
		return print(self.memory)