from cpu import Cpu

def main():
	cpu = Cpu()
	cpu.LoadGame('test_opcode.ch8')
	cpu.StartGame()



if __name__ == '__main__':
	main()
