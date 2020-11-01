from ram_memory import RamMemory
from v_registers import VRegisters
from stack import Stack
from random import randint
from screen import Screen
import pygame

class Cpu:
	def __init__(self):
		self.Inicialize()


	############################FUNÇÃO QUE INICILIZA A CPU, MEMORIA RAM E OS REGISTRADORES############################
 
	def Inicialize(self):
		self.ram_memory = RamMemory()					#CRIA A MEMORIA 8*4096 BITS / RESETA
		self.pc = 512									#DETERMINA O CONTADOR  PRO ENDEREÇO 0X200 / RESETA
		self.v = VRegisters()							#CRIA OS REGISTRADORES V 8*16 BITS / RESETA
		self.i = 0										#ZERA O REGISTRADOR I / RESETA
		self.delay_timer = 0							#DELAY TIMER DECREMENTA DE 60HZ ATÉ 0 / RESETA
		self.sound_timer = 0							#SOUND TIMER DECREMENTA DE 60HZ ATÉ 0 / RESETA
		self.sp = 0										#ZERA O APONTADOR DE PILHA / RESETA
		self.stack = Stack()							#CRIA UMA PILHA 16*16 BITS / RESETA
		self.key = [False for i in range(16)] 			#CRIA lISTA DE TECLAS PRECIONADAS (MAXIMO 16 TECLAS)
		self.LoadFonts()								#CARREGA AS FONTS PARA A MEMORIA 
		self.screen = Screen()							#INICIALIZA A TELA
		self.DELAYSOUNDTIMER = pygame.USEREVENT + 1 	#EVENTO DO PYGAME PARA TIMER 60HZ E ATUALIZAR A TELA
		self.sound = True								#PERMITE QUE O SOM SEJA TOCADO

		pass

	#####################################CARREGA O JOGO PARA A MEMORIA RAM ########################################################

	def LoadGame(self, rom: str):
		idx = 0x200 						#ENDEREÇO NO QUAL A CPU LÊ O JOGO

		with open(rom, 'rb') as file:		#ABRI O ARQUIVO EM BYTES
			while 1:						#ENQUANTO INFINITO
				byte = file.read(1)			#LER BYTE A BYTE
				if not byte:				#COMPARA SE É UM BYTE SE NÃO FOR CHEGAMOS NO FINAL DO ARQUIVO
					break
				self.ram_memory.WriteValue(idx, int.from_bytes(byte, "big", signed=False))#ARMAZENADO NO IDX DA MEMORIA O VALOR LIDO
				idx += 1					#AUMENTAR O IDEX CONTADOR

	#############################################INICIA O JOGO######################################################################

	def StartGame(self):
		self.screen.startScreen()							#INICIA A TELA

		pygame.time.set_timer(self.DELAYSOUNDTIMER, round((1/60)*1000))

		self.started = True 								#VARIAVEL QUE INDICA SE O JOGO FOI INICIADO

		while self.started:									#VERIFICA SE O JOGO INICIOU
			
			self.listen()
			self.ExecuteOpcode(self.GetCurrentOpcode())     #CARREGA AS INSTRUÇÕES DO JOGO
			pygame.time.delay(round((1/1024)*1000))			#DELAY PARA EXECUTAR OS OPCODES NA VELOCIDADE CORRETA

		pygame.quit()
	########################################################################################################

	def timeout60Hz(self): 	# PARA SER CHAMADO NA FREQUENCIA DE  60Hz. DECREMENTA OS TIMERS DO EMULADOR E ATUALIZA A TELA

		if(self.delay_timer > 0): 	# DECREMENTAMOS O VALOR DO DELAY SE ELE NAO FOR 0
			self.delay_timer -= 1

		if(self.sound_timer > 0): 	#MESMA COISA COM O SOUND
			self.sound_timer -= 1
			if self.sound: 	# E SE NAO FOR 0 E NOS ESTAMOS PERMITINDO QUE SOM SEJA TOCADO, TOCAMOS O BEEP!
				self.screen.beep.play()

		if self.started: 																																		# Same with our memory
			self.screen.refreshScreen()#	#ATUALIZA A TELA																		

	#####################################################################################################################

	######################################RETORNA O ATUAL OPCODE DO PC###################################################

	def GetCurrentOpcode(self):
		# O OPCODE É CONSTITUIDO DE 2 BYTES ENTÃO PRECISAMOS LER O BYTE DO PC E SOMAR COM PROXIMO BYTE
		# PARA FAZER ISSO É PRECISSO FAZER UMA OPERAÇÃO DE BITWISE (<< / DESLOCAMENTO A ESQUERDA )
		# PARA TRANSFORMAR  1 BYTE EM 2 BYTES
		# E DEPOIS FAZER A OPERAÇAO DE (OU) PARA SOMARMOS O ULTIMO BYTE QUE É 0 COM O PROXIMO BYTE
		# VAMOS SUPOR QUE O PRIMEIRO BYTE CARREGADO SEJA (0XA2) E O SEGUNDO (0XF0)
		# ENTAO IREMOS ADICIONAR 8 BITS A ESQUERDA FAZENDO ISSO O BYTE (0xA2) SE TORNA 2 BYTES(0xA200))
		# COMO ADICIONAMOS 8 BITS 0  OS 8 PRIMEIROS PERMANECERAM IGUAIS
		# SÓ QUE NAO QUEREMOS ISSO E SIM A JUNÇÃO DO PRIMEIRO BYTE COM O SEGUNDO
		# 
		#-------------bin----------------hex----------operação----
		#			1010010     		0xA2    		<< 8 	
		# Resultado 101001000000000		0xA200
		

		# AGORA FAZEMOS A OPERAÇÃO (OU) PARA QUE POSSAMOS JUNTAR OS BYTES
		# COM ESSA OPERAÇÃO ONDE TIVER 1 É VERDADEIRO ENTAO O RESULTADO É 1
		# DEPOIS DISSO TEMOS 2 BYTES E AGORA SIM OBTEMOS O (OPCODE/INSTRUÇÃO)


		#----------------bin----------------hex----------operação----
		#				101001000000000     0xA2    		<< 8 	
		#               	  111100000		0XF0 			 | (ou) 
		# Resultado 	101001111100000		0xA2F0
		return ((self.ram_memory.ReadValue(self.pc) << 8) | self.ram_memory.ReadValue(self.pc + 1)) #CARREGA A INSTRUÇÃO

######################################EXECUTA OS OPCODES###################################################

	def ExecuteOpcode(self, opcode):
		#AQUI DEVEMOS FAZER UM MASCARAMENTO IGUAL FIZEMOS ACIMA PARA SABERMOS O VALOR DE CADA 4 BIT

		a   =  (opcode  &  0xF000) 		 #VALOR DO ID DO OPCODE
		x   =  (opcode  &  0x0F00) >> 8  #VALOR DO REGISTRADOR VX
		y   =  (opcode  &  0x00F0) >> 4  #VALOR DO REGISTRADOR VY
		n   =  (opcode  &  0x000F)       #VALOR DE N  - 4 BIT
		nn  =  (opcode  &  0x00FF)       #VALOR DE NN - 8 BIT
		nnn =  (opcode  &  0x0FFF)		 #VALOR DO ENDEREÇO 
		


		if (a == 0x0000): 				 #OPCODE (0NNN) CHAMA A ROTINA
										 #NÃO NESSESÁRIO NA MAIORIIA DAS ROMS

			a = (opcode & 0x00FF)
			if (a == 0x00E0): 		 	#OPCODE (00E0) LIMPA A TELA.
				self.screen.clear()
				self.pc += 2 


			elif (a == 0x00EE): 		 #OPCODE (00EE) RETORNA DE UMA SUBROTINA 
				if self.sp > 0:		 #VERIFICA SE O (SP) É MAIOR DO QUE ZERO. ASSIM ELE NAO FICA NEGATIVO
					self.sp -= 1		 #SE FOR MAIOR DO QUE ZERO, (SP) VOLATA PARA POSISAO ANTERIOR
					self.pc = self.stack.ReadValue(self.sp)  #ARNAZENA NO (PC) O ENDEREÇO DA ULTIMA INSTRUÇÃO
					self.pc += 2 		 #ARMAZENA NO (PC) O ENDEREÇO DA PROXIMA INSTRÇAO 
					


		elif (a == 0x1000): 					#OPCODE (1NNN) PULA PARA O ENDEREÇO ESPECIFICO
			self.pc = nnn						#ARMAZENA NO (PC) O ENDEREÇO DE (NNN)
			


		elif(a == 0x2000): 							#OPCODE (2NNN) CHAMA UMA SUBROTINA. 
			self.stack.WriteValue(self.sp, self.pc)	#ENTÃO TEMOS QUE ARMAZENAR NOSSO ENDERÇO ATUAL DO (PC) NA PILHA.
			self.sp += 1							#DEPOIS DISSO PRECISAMOS INCREMENTAR O (SP)PARA QUE SOBRESCREVER A PILHA ATUAL 
			self.pc = nnn 							#ARMAZENA O ENDEREÇO APONTADO DA SUBROTINA.
			

		elif(a == 0x3000): 						#OPCODE (3XNN) SE (VX) FOR IGUAL A (NN) PULA A PROXIMA INSTRUÇÃO, SE NAO CONTINUA.
			if self.v.ReadValue(x) == nn:		#VERIFICA SE (VX) É IQUAL A NN
				self.pc += 4					#ARMAZENA NO (PC) O ENDEREÇO POSTERIOR DA PROXIMA INSTRUÇÃO
			else:
				self.pc += 2					#ARMAZENA NO (PC) A PROXIMA INSTRUÇÃO


		elif ( a == 0x4000 ): 					# OPCODE (4XNN) SE (VX) NAO FOR IGUAL A (NN) PULA A PROXIMA INSTRUÇÃO, SE FOR CONTINUA
			if self.v.ReadValue(x) != nn:		#VERIFICA SE (VX) NÃO É IQUAL A (NN)
				self.pc += 4					#ARMAZENA NO (PC) O ENDEREÇO POSTERIOR DA PROXIMA INSTRUÇÃO
			else:
				self.pc += 2					#ARMAZENA NO (PC) A PROXIMA INSTRUÇÃO
				
			

		elif ( a == 0x5000 ): 								   # OPCODE (5XY0) SE (VX)  FOR IGUAL A (VY) PULA A PROXIMA INSTRUÇÃO, SE NAO CONTINUA
			if (self.v.ReadValue(x) ==  self.v.ReadValue(y)):  #VERIFICA SE (VX)  É IQUAL A (VY)
				self.pc += 4								   #ARMAZENA NO (PC) O ENDEREÇO POSTERIOR DA PROXIMA INSTRUÇÃO
			else:
				self.pc += 2								   #ARMAZENA NO (PC) A PROXIMA INSTRUÇÃO


		elif (a == 0x6000):					#OPCODE (6XNN) SETA O VALOR DE (NN) (VX)
			self.v.WriteValue(x, nn)				#DEFINE O VALOR DE (NN) NO (VX)
			self.pc += 2							#ARMAZENA NO (PC) A PROXIMA INSTRUÇÃO


		elif (a == 0x7000):  								#OPCODE (7XNN) ADICIONAR O VALOR DE NN  AO (VX)
			self.v.WriteValue(x, (self.v.ReadValue(x) + nn))	#ADICIONA (NN) AO (VX)
			self.pc += 2										#ARMAZENA NO (PC) A PROXIMA INSTRUÇÃO

			

		elif (a == 0x8000):

			a = opcode & 0x000F
			if (a == 0x0000): 								#OPCODE (8XY0) SETAR O VALOR DE (VX) POR (VY)
				self.v.WriteValue(x, self.v.ReadValue(y))		#DEFINIR (VY) NO (VX)
				self.pc += 2									#ARMAZENA NO (PC) A PROXIMA INSTRUÇÃO

			elif (a == 0x0001):												#OPCODE (8XY1) SETAR O VALOR DE (VX) POR ( (VX) ( | ou ) (VY) ) 
				self.v.WriteValue(x, (self.v.ReadValue(x) | self.v.ReadValue(y))) 	#DEFINE AO (VX) PELO RESULTADO DE (VX | VY)
				self.pc += 2														#ARMAZENA NO (PC) A PROXIMA INSTRUÇÃO


			elif (a == 0x0002):												#OPCODE (8XY2) SETAR O VALOR DE (VX) POR ( (VX) ( & and ) (VY) ) 
				self.v.WriteValue(x, (self.v.ReadValue(x) & self.v.ReadValue(y)))		#DEFINE AO (VX) O RESULTADO DE (VX & VY)	
				self.pc += 2														#ARMAZENA NO (PC) A PROXIMA INSTRUÇÃOS

			elif (a == 0x0003):												#OPCODE (8XY3) SETAR O VALOR DE (VX) POR ( (VX) ( ^ xor ) (VY) )
				self.v.WriteValue(x, (self.v.ReadValue(x) ^ self.v.ReadValue(y)))	#DEFINE AO (VX) O RESULTADO DE (VX ^ VY)
				self.pc += 2														#ARMAZENA NO (PC) A PROXIMA INSTRUÇÃOS


			elif (a == 0x0004):												#OPCODE (8XY4) ADICONAR O VALOR (VY) AO (VX) E ARMAZENA 1 AO (VF) SE AO ADICIONAR O VALOR SEJA MAIOR QUE (8 BITS) SE NAO  (VF) ARMAZENA (0)  
				self.v.WriteValue(0xF, 0)									#RESETANDO O (VF)
				if ((self.v.ReadValue(x) + self.v.ReadValue(y)) > 0xFF ):	#DEFININDO 1 PARA CARRY
					self.v.WriteValue(0xF, 1)
				self.v.WriteValue(x , (self.v.ReadValue(x) + self.v.ReadValue(y)))  #DEFININDO O VALOR DE (VY + VX) AO (VY)
				self.pc += 2												#ADICIONA AO (PC) A PROXIMA INSTRUÇÃO
				 

			elif (a == 0x0005):									#OPCODE (8XY5) (VY) É SUBTRAIDO DE (VX) E (VF) RECEBE (0) SE TIVER EMPRESTIMO SE NAO RECEBE  (1)
				self.v.WriteValue(0xF, 1)							#RESETANDO O EMPRESTIMO
				if (self.v.ReadValue(x) < self.v.ReadValue(y)):	#VERIFICA SE NÃO A EMPRESTIMO
					self.v.WriteValue(0xF, 0)					#ATRIBUI FALSO AO EMPRESTIMO
				self.v.WriteValue(x, (self.v.ReadValue(x) - self.v.ReadValue(y))) #SUBTRAI VALOR DE (VY) POR (VX) 
				self.pc += 2									#ADICIONA AO (PC) A PROXIMA INSTRUÇÃO


			elif (a == 0x0006):									#OPCODE (8XY6) ARMAZENA O BIT MENOS SIGNIFICATIVO DE (VX) EM VF. DEPOIS DESLOCA (VX) (1) A DIREITA
				self.v.WriteValue(0xF, (self.v.ReadValue(x) & 0x1)) #ARMAZENANDO LSB EM (VF)
				self.v.WriteValue(x, (self.v.ReadValue(x) >> 1)) 		#ARMAZENANDO (VX >> 1) EM (VX)
				self.pc += 2

			elif (a == 0x0007):									#OPCODE (8XY7) ARMAZENAR (VY - VX) EM (VX) E ARMAZENAR EM (VF) (0) SE TIVER EMPRESTIMO SE NAO ARMARZENA (1)
				self.WriteValue(0xF, 1)							#RESETANDO O EMPRESTIMO
				if (self.v.ReadValue(x) < self.v.ReadValue(y)):	#VERIFICA SE NÃO A EMPRESTIMO
					self.v.WriteValue(0xF, 0)					#ATRIBUI FALSO AO EMPRESTIMO
				self.v.WriteValue(x, (self.v.ReadValue(y) - self.ReadValue(x))) #ARMAZENA VALOR DE (VY - VX) EM (VX) 
				self.pc += 2									#ADICIONA AO (PC) A PROXIMA INSTRUÇÃO

			elif (a == 0x000E):										#OPCODE (8XYE) ARMAZENE O BIT MAIS SIGNIFICATIVO EM DE (VX) EM (VF) E DEPOIS DESLOCA (VX) (1) A ESQUERDA
				self.v.WriteValue(0xF, (self.v.ReadValue(x) >> 7))  #ARMAZENANDO MSB EM (VF)
				self.v.WriteValue(x, (self.v.ReadValue(x) << 1)) 		#ARMAZENANDO (VX << 1) EM (VX)
				self.pc += 2										#ADICIONA AO (PC) A PROXIMA INSTRUÇÃO


		elif (a == 0x9000):									#OPCODE (9XY0) PULA A PROXIMA INSTRUÇÃO SE (VX) NAO FOR IGUAL A (VY)
			if (self.v.ReadValue(x) != self.v.ReadValue(y)):	#VERIFICA SE (VX) NAO É IGUAL A (VY)
				self.pc += 4									#ADICIONA AO (PC) A INSTRUÇÃO POSTERIOR A PROXIMA INSTRUÇÃO
			else:												#SE (VX) FOR IGUAL A (VY)
				self.pc += 2									#ADICIONA AO (PC) A PROXIMA INSTRUÇÃO


		elif (a == 0xA000):					#OPCODE (ANNN) ARMAZENAR EM (I) O ENDEREÇO (NNN)
			self.i = nnn 					#ARMAZENA EM (I) O ENDEREÇO DE (NNN)
			self.pc += 2					#ADICIONA AO (PC) A PROXIMA INSTRUÇÃO


		elif (a == 0xB000):							#OPCODE (BNNN) PULA PRA O ENDEREÇO (V0) + (NNN)
			self.pc = (self.v.ReadValue(0x0) + nnn) #ARMAZENA AO (PC) O ENDEREÇO (NN) MAIS O VALOR DE (V0) 
		elif (a == 0xC000):								#OPCODE (CXNN) ARMRZENAR EM (VX) O VALOR DE (NUMERO ALEATORIO & NN)
			self.v.WriteValue(x, (randint(0,255) & nn))	#ARMAZENA AO (VX) DO RESULTADO DE (VALOR ALEATORIO & VY)
			self.pc += 2 								#ADICIONA AO (PC) A PROXIMA INSTRUÇÃO
			

		elif (a == 0xD000):					#OPCODE (DXYN) EXIBE UM SPRITE DE COMPRIMENTO (N) NAS CORDENADAS (V [X], V [Y]) DA MEMORIA COMENÇANDO EM (I)
			self.v.WriteValue(0xF, 0)		#ARMAZENA (0) POR PADRAO E (1) SE DURANTE A INTRUNÇÃO APAGARMOS UM PIXEL (TORNANDO ELE PRETO OU 0)

			for i in range(n): 	# PARA CADA LINHA DO  NOSSO SPRITES
				line = self.ram_memory.ReadValue((self.i+i)) 	# ESTAMOS LENDO CADA LINHA DO SPRITE COMENÇANDO DO ENDEREÇO (I) E INCREMENTANDO  ELE CADA LINHA
				currentY = self.v.ReadValue(y) + i 		# SETMAOS A POSIÇAO INICIAL DE (Y) PARA O (VY) E ADCIONANDO O CONTADOR I PARA PODERMOS PEGAR A ATUAL POSIÇÃO DA LINHA

				if currentY < len(self.screen.pixels[0]): 	# SE TEM ALTURA DISPONIVEL NA TELA

					for j in range(8): 	# UM SPRITE DE CUMPRIMENTO DE 8 BITS

						currentX = self.v.ReadValue(x) + j 	# SETANDO A ATUAL POSIÇÃO X PARA O VALOR DE  V[X] E ADICIONANDO O CONTADOR J
						if currentX < len(self.screen.pixels): 	# SE TEM LARGURA DISPONIVEL NA TELA

							mask = 0x1 << (7-j) 										# MASCARA QUE SERA USADA PARA RECUPERAR BIT DA LINHA (QUE É UM BYTE). SE EU QUISER O (MSB), J ESTA EM 0, ENTAO NOS TEMOS A MASCARA DE 0b10000000. APLICANDO ELE COM O BITWISE (&) E DESLOCANDO IREMOS RECEBER NOSSO BIT.
							newBit = (mask & line) >> (7-j) 							# PEGANDO O BIT COM A MASCARA , E DESLOCANDO ELE DE VOLTA PARA A POSIÇÃO (LSB) 
							result = newBit ^ self.screen.pixels[currentX][currentY] 	# A new pixel is decided by doing a XOR between the current state of the pixel, and the value wanted by the sprite
							self.screen.pixels[currentX][currentY] = result 			# We set the result of the XOR to the screen

							if(self.screen.pixels[currentX][currentY] == 0 and newBit == 1): 	# If we erased it (with a XOR, it happens when the pixel is erased and we wanted to apply a value of 1)
								self.v.WriteValue(0xF, 1) 
							
			self.pc += 2

		elif (a == 0xE000):
			a = opcode & 0x000F
			if (a == 0x000E):									#OPCODE (EXYE) PULA A PROXIMA INSTRUÇÃO SE A TECLA ARMAZENADA EM (VX) FOR PRESSIONADA
				if (self.key[self.v.ReadValue(x)] == True): 	#VERIFICA SE A TECLA ARMAZENADA EM (VX) ESTA PRECIONADA
					self.pc += 4								#ARMAZENA NO (PC) O ENDEREÇO DA INSTRUÇÃO POSTERIOR A PROXIMA INSTRUÇÃO
				else:											#SE A TECLA NÃO ESTIVER PRECIONADA CONTINUA
					self.pc += 2								#ARMAZENA NO (PC) O ENDEREÇO DA PROXIMA INSTRUÇÃO

			elif (a == 0x0001):									#OPCODE (EXY1) PULA A PROXIMA INSTRUÇÃO SE A TECLA ARMAZENADA EM (VX) FOR PRESSIONADA
				if (self.key[self.v.ReadValue(x)] == False): 	#VERIFICA SE A TECLA ARMAZENADA EM (VX) ESTA PRECIONADA
					self.pc += 4								#ARMAZENA NO (PC) O ENDEREÇO DA INSTRUÇÃO POSTERIOR A PROXIMA INSTRUÇÃO
				else:											#SE A TECLA NÃO ESTIVER PRECIONADA CONTINUA
					self.pc += 2								#ARMAZENA NO (PC) O ENDEREÇO DA PROXIMA INSTRUÇÃO

		elif (a == 0xF000):
			a = opcode & 0x00FF
			if (a == 0x0007):							#OPCODE FX007:
				self.v.WriteValue(x, self.delay_timer)	#ARMAZENA AO (VX) O VALOR DO (DELAY TIMER)
				self.pc += 2							#ADICIONA AO (PC) A PROXIMA INSTRUÇÃO

			elif (a == 0x000A):							#OPCODE FX00A
				self.v.WriteValue(x, self.sound_timer)	#ARMAZENA AO (VX) O VALOR DE (SOUND TIMER)
				self.pc += 2 							#ADICIONA AO (PC) A PROXIMA INSTRUÇÃO

			elif (a == 0x0015):							#OPCODE FX015:
				self.delay_timer = self.v.ReadValue(x)  #ADIOCIONA AO (DELAY TIMER) O VALOR DE (VX)
				self.pc += 2 							#ADICIONA AO (PC) A PROXIMA INSTRUÇÃO

			elif (a == 0x0018):							#OPCODE FX018:
				self.sound_timer = self.v.ReadValue(x)  #ADIOCIONA AO (SOUND TIMER) O VALOR DE (VX)
				self.pc += 2 							#ADICIONA AO (PC) O ENDEREÇO DA PROXIMA INSTRUÇÃO

			elif (a == 0x001E):								#OPCODE FX01E: ADICIONAR A (I) O VALOR DE (VX) SE ESSA ADIÇÃO FOR UMA PALAVRA MAIOR QUE 8 BITS (VF) RECEBE (1) SE NAO RECEBE (0) 
				if ((self.i + self.v.ReadValue(x)) > 0xFF): #VERFICA SE A ADIÇÃO ESTOURA (8 BITS)
					self.v.WriteValue(0xF, 1)				#ARMAZENA (1) AO (VF)	
				else:										#SE NAO ESTOURAR
					self.v.WriteValue(0xF, 0)				#ARMAZENA (0) AO (VF)
				self.i = (self.i + self.v.ReadValue(x))		#ARMAZENA EM (I) A SOMA DE (I + VX)
				self.pc += 2								#ADICIONA AO (PC) O ENDEREÇO DA PROXIMA INSTRUÇÃO


			elif (a == 0x0029):							#OPCODE FX029: ARMAZENA AO I A POSIÇÃO DO CARACTERE EM (VX)
				self.i = (self.v.ReadValue(x) * 0x5)	#ARMAZENA EM (I) A POSIÇÃO DO CARACTERE EM (VX) * 5, PORQUE UM CARACTERE É COMPOSTO POR (5 BYTES) NA MEMORIA. SE O CARACTERE EM (VX) FOR (3) ELE APONTARIA PARA O ENDEREÇO (OX3) QUE ESTA 0 (3°BYTE) DO CARACTERE (0). ETAO (*0x5) O (3) SE TORNA (15) QUE É (1° BYTE) DO CARATERE (3)
				self.pc += 2							#ADICIONA AO (PC) O ENDEREÇO DA PROXIMA INSTRUÇÃO

			elif (a == 0x0033):							#OPCODE FX033: ARMAZENA A REPRESENTAÇÃO DECIMAL CODIFICADA BINARIA (BCD) DE VX EM I. OU SEJA O (BCD) CONSISTE EM ARMAZENAR UM VALOR DECIMAL EM BINARIO SEPARADAMENTE EX: (321) PREICISAMOS ARMAZENAR O (3) NO (I) O DOIS NO (I+1) E O 1 NO (I+2) 
				self.ram_memory.WriteValue(self.i,(self.v.ReadValue(x) // 100))		#DIVIDI O VALOR POR 100 PARA ENCONTRAMOS O PRIMEIRO NUMERO EX: 321 / 100 = 3
				self.ram_memory.WriteValue(self.i + 1, (self.v.ReadValue(x) - (self.ram_memory.ReadValue(self.i)*100)) // 10 ) #DIMINUI O VALOR ORIGINAL PELO VALOR DIVIDO POR 100 MULTIPLLICATICADO POR 100 E DIVIDE POR 10  PARA ENCONTRAR O NUMERO DO MEIO EX: 321 - (3*100)300 = 21 /10 = 2 
				self.ram_memory.WriteValue(self.i + 2, self.v.ReadValue(x) - (self.ram_memory.ReadValue(self.i)*100) - (self.ram_memory.ReadValue(self.i+1)*10)) #MESMA COISA PRA ENCRONTAR O DO MEIO SO QUE ACRESENTA A OPERAÇAO DO MEIO Ex: 321 - (3*100)300 - (2*10)20 = 1 
				self.pc +=  2		#ADICIONA AO (PC) O ENDEREÇO DA PROXIMA INSTRUÇÃO
			elif (a == 0x0055):							#OPCODE FX055: ARMAZENA EM (I) O VALOR DE (V0) ATE O VALOR DE (VX) INCLUINDO (VX) DEPOIS DESSA OPERAÇÃO O (I) ADICIONA (VX) + (1)
				for i in range(0,x+1):
					self.ram_memory.WriteValue(self.i+i, self.v.ReadValue(i))
				self.i = x + 1
				self.pc +=  2							#ADICIONA AO (PC) O ENDEREÇO DA PROXIMA INSTRUÇÃO


			elif (a == 0x0065):							#OPCODE FX065: PRENCHER DO (V0) AO (VX) COM VALORES DA  MEMORIA COMEÇANDO DO VALOR (I)
				for i in range(0,x+1):
					self.v.WriteValue(i,self.ram_memory.ReadValue(self.i+i))
				self.i = x + 1
				self.pc +=  2							#ADICIONA AO (PC) O ENDEREÇO DA PROXIMA INSTRUÇÃO


	##############################################################################################################################

	def LoadFonts(self):#ESCREVE NO COMEÇO DA MEMORIA RAM DO VALOR 0X0 AO 0x4F AS FONTES ULTIZADA 
	#CADA FONTE És COMPOSTA POR 5 LINHAS E 4 PIXELS E CADA UM É ARMAZENADA EM 5BYTES SENDO OS PRIMEIROS 4 BITS
	#QUE REPRESENTA OS PIXELS E OS OUTROS 4 BITS SAO ZERADOS
		self.fonts = [

		0xF0, 0x90, 0x90, 0x90, 0xF0, 	# 0
		0x20, 0x60, 0x20, 0x20, 0x70, 	# 1
		0xF0, 0x10, 0xF0, 0x80, 0xF0, 	# 2
		0xF0, 0x10, 0xF0, 0x10, 0xF0, 	# 3
		0x90, 0x90, 0xF0, 0x10, 0x10, 	# 4
		0xF0, 0x80, 0xF0, 0x10, 0xF0, 	# 5
		0xF0, 0x80, 0xF0, 0x90, 0xF0, 	# 6
		0xF0, 0x10, 0x20, 0x40, 0x40, 	# 7
		0xF0, 0x90, 0xF0, 0x90, 0xF0, 	# 8
		0xF0, 0x90, 0xF0, 0x10, 0xF0, 	# 9
		0xF0, 0x90, 0xF0, 0x90, 0x90, 	# A
		0xE0, 0x90, 0xE0, 0x90, 0xE0, 	# B
		0xF0, 0x80, 0x80, 0x80, 0xF0, 	# C
		0xE0, 0x90, 0x90, 0x90, 0xE0, 	# D
		0xF0, 0x80, 0xF0, 0x80, 0xF0, 	# E
		0xF0, 0x80, 0xF0, 0x80, 0x80 	# F

		]

		for idx, val in enumerate(self.fonts):			#PERCORRE CADA BYTE DA FONTE
			self.ram_memory.WriteValue(idx, val)		#ESCREVE CADA BYTE EM SEU DEVIDO LOCAL

	###################################################################################################################################################

	def listen(self):
		for event in pygame.event.get(): 	# PARA CADA EVENTO NA LISTA

				if event.type == pygame.QUIT: 						# QUIT
					self.started = False 	#PARAMOS O JOGO
				
				elif event.type == self.DELAYSOUNDTIMER: 	# TIMER DE 60Hz
					self.timeout60Hz() 	# FUNÇÃO QUE ATUALIZA A TELA E GERENCIA OS TIMERS

				elif event.type == pygame.VIDEORESIZE: 			# REDIMENCIONA A TELA
					self.screen.resizeScreen(event.w, event.h) 	# FUNÇÃO QUE REDIMENCIONA A TELA E RESETA
					
				elif event.type == pygame.KEYDOWN: 				# PRESSIONANDO UMA TECLA
					
					# GAME KEYS
					# QUANDO UMA TECLA É PRESSIONADA ATRIBUIMOS O VALOR 1
					if event.key == pygame.K_1:
						self.key[0x1] = 1
					elif event.key == pygame.K_2:
						self.key[0x2] = 1
					elif event.key == pygame.K_3:
						self.key[0x3] = 1
					elif event.key == pygame.K_4:
						self.key[0xC] = 1
					elif event.key == pygame.K_q:
						self.key[0x4] = 1
					elif event.key == pygame.K_w:
						self.key[0x5] = 1
					elif event.key == pygame.K_e:
						self.key[0x6] = 1
					elif event.key == pygame.K_r:
						self.key[0xD] = 1
					elif event.key == pygame.K_a:
						self.key[0x7] = 1
					elif event.key == pygame.K_s:
						self.key[0x8] = 1
					elif event.key == pygame.K_d:
						self.key[0x9] = 1
					elif event.key == pygame.K_f:
						self.key[0xE] = 1
					elif event.key == pygame.K_z:
						self.key[0xA] = 1
					elif event.key == pygame.K_x:
						self.key[0x0] = 1
					elif event.key == pygame.K_c:
						self.key[0xB] = 1
					elif event.key == pygame.K_v:
						self.key[0xF] = 1

					# MENU KEYS
					elif event.key == pygame.K_ESCAPE:
						self.started = False
					elif event.key == pygame.K_F1:
						self.started = False
						self.changeRom = True
					elif event.key == pygame.K_F2:
						self.rebootGame()
					elif event.key == pygame.K_F3:
						self.paused = not self.paused
						self.screen.togglePause(self.paused)
					elif event.key == pygame.K_F4:
						self.nextStep = True
					elif event.key == pygame.K_F5:
						self.sound = not self.sound

				elif event.type == pygame.KEYUP:
					
					# GAME KEYS
					# QUANDO A TECLA É SOLTA ATRIBUIMOS O VALOR 0 
					if event.key == pygame.K_1:
						self.key[0x1] = 0
					elif event.key == pygame.K_2:
						self.key[0x2] = 0
					elif event.key == pygame.K_3:
						self.key[0x3] = 0
					elif event.key == pygame.K_4:
						self.key[0xC] = 0
					elif event.key == pygame.K_q:
						self.key[0x4] = 0
					elif event.key == pygame.K_w:
						self.key[0x5] = 0
					elif event.key == pygame.K_e:
						self.key[0x6] = 0
					elif event.key == pygame.K_r:
						self.key[0xD] = 0
					elif event.key == pygame.K_a:
						self.key[0x7] = 0
					elif event.key == pygame.K_s:
						self.key[0x8] = 0
					elif event.key == pygame.K_d:
						self.key[0x9] = 0
					elif event.key == pygame.K_f:
						self.key[0xE] = 0
					elif event.key == pygame.K_z:
						self.key[0xA] = 0
					elif event.key == pygame.K_x:
						self.key[0x0] = 0
					elif event.key == pygame.K_c:
						self.key[0xB] = 0
					elif event.key == pygame.K_v:
						self.key[0xF] = 0

		########################################################################################################
