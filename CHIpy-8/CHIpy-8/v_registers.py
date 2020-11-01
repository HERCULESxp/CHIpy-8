from unsignedbitsarray import UnsignedBitsArray


class VRegisters:
	def  __init__(self):
		self.v = UnsignedBitsArray(8, 16) #CRIA A MEMORIA DOO REGISTRADOR COM 16 BYTES E VAZIA

	def WriteValue(self, idx, value):#ESCREVE  DADOS NO REGISTRADOR 
		self.v[idx] = value

	def ReadValue(self, idx):#LER DADOS DO REGISTRADOR
		return self.v[idx]
		
	def ClearRegister():#ESVAZIA O REGISTRADOR
		pass

	def ShowValues(self):#MOSTRA OS VALORE DO REGISTRADOR (PARA DEBUG)
		return print(self.v)