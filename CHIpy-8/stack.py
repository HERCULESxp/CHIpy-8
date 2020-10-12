from unsignedbitsarray import UnsignedBitsArray


class Stack:
	def  __init__(self):
		self.stack = UnsignedBitsArray(16, 16) #CRIA A MEMORIA DA PILHA COM 32 BYTES E VAZIA

	def WriteValue(self, idx, value):#ESCREVE  DADOS NA PILHA
		self.stack[idx] = value

	def ReadValue(self, idx):#LER DADOS DA PILHA
		return self.stack[idx]
	def ClearRegister():#ESVAZIA A PILHA
		pass

	def ShowValues(self):#MOSTRA OS VALORE DA PILHA (PARA DEBUG)
		return print(self.stack)