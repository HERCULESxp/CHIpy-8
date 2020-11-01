import pygame


class Screen: #CLASSE QUE INTERAGE COM A TELA

	def __init__(self, Upscaling = 10 ):

		self.upscaling = Upscaling
		self.Xsize = 64 #NUMERO ORIGINAL DE PIXELS EM X
		self.Ysize = 32	#NUMERO ORIGINAL DE PIXELS EM Y

		self.SXsize = 0	#NUMERO DE PIXELS PARA TELA EM X
		self.SYsize = 0 #NUMERO DE PIXELS PARA TELA EM X

		self.pixels = [] #MAPA DA TELA INICIAL EM PIXELS
		self.clear() 	 #INICIALIZANDO UMA LISTA 2D DE PIXELS LIMPANDO A TELA

		self.white = (255, 255, 255) 	# DEFININDO A COR BRANCA
		self.black = (0, 0, 0) 			# DEFININDO A COR PRETA
		
		pygame.init() #INICIALIZANDO PYGAME
		self.beep = pygame.mixer.Sound("beep.ogg") #CARRENDO O BEEP 
		self.font = pygame.font.Font(pygame.font.get_default_font(), 14) #CARREGA A FONTE

	########################################################################################################

	def clear(self): 	# APAGA A DELA RESETANDO A LISTA DE PIXELS 2D POR 0
		# UMA LISTA 2D REPRESENTANDO OS PIXELS DO GAME COM O FORMATO DE PIXELS[X][Y]
		self.pixels = [[0]*self.Ysize for i in range(self.Xsize)]

	########################################################################################################

	def startScreen(self): 	# INICIALIZA A JANELA DO JOGO E SETA UM UPSCALING PORQUE A JANELA É REDIMENCIONAVEL

		self.SXsize = (self.Xsize * self.upscaling)	# CALCULA O TAMANHO DA TELA COM UM UPSCALING
		self.SYsize = (self.Ysize * self.upscaling)

		self.window = pygame.display.set_mode((self.SXsize, self.SYsize), pygame.RESIZABLE) 	# INICIALIZA A JANELA COM O PYGAME E ATIVA O UPSCALING
		pygame.display.set_caption("CHIpy-8 Emulator by Hércules Mendes") 	#TITULO DA JANELA

		#pygame.draw.lines(self.window, self.white, False, [(0,self.Ysize*self.upscaling), (self.Xsize*self.upscaling, self.Ysize*self.upscaling), (self.Xsize*self.upscaling, 0)])
		self.refreshScreen() 				# ATUALIZA A TELA 


	########################################################################################################
	def refreshScreen(self): #ATUALIZA A TELA 
		for x in range(0, self.Xsize): 			# PARA CADA X
			for y in range(0, self.Ysize):		# PARA CADA Y
				if(self.pixels[x][y] == 0): 	# SE O PIXEL  É 0 (PRETO)
					color = self.black 			# A COR ESCOLHIDA SERA DEFINIDA PELA NOSSA COR PRETA
				else:
					color = self.white 			# SE O PIXEL NÃO FOR 0 (ENTAO 1 OR QUALQUER QUALQUER VALOR NAO INTENCIONAL QUE NAO TEVERIA ESTA ACONTECENDO)NOS DEFINIMOS COM A NOSSA COR BRANCA

				#NÓS DESENHAMOS NOSSO PIXEL SCALONADO , QUÉ SOMENTE UM QUADRADO COMO O TAMANHO DO NOSSO UPSCALING INICIANDO COM A POSIÇÃO LEVANDO EM CONTA O VALOR DO UPSCALING
				#ESTAMOS USANDO A NOSSA COR USADA ANTERIORMENTE NO IF 
				pygame.draw.rect(self.window, color, (self.upscaling*x, self.upscaling*y, self.upscaling, self.upscaling))

		pygame.display.flip() 	# ATUALIZA A TELA
	########################################################################################################
	def resizeScreen(self, newX, newY): 	# CALCULA A NOVA ESCALA DA TELA QUANDO É REDIMENCIONADA E RESETA
		newX = (newX // self.Xsize) 
		newY = (newY // self.Ysize)
		self.upscaling = min(newX, newY) 	# SELECIONANDO O MINIMO DE ESCALA X E DE Y EM ORDEM PARA NAO INCREMENTAR O TAMANHO DA NOVA JANELA
		self.startScreen() 							#RESETA A TELA COM A NOVA ESCALA

	########################################################################################################