"""CPU functionality."""

import sys, re

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
AND = 0b10101000
NOT = 0b01101001
OR = 0b10101010
MOD = 0b10100100
SHL = 0b10101100
SHR = 0b10101101
XOR = 0b10101011

SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 7 + [0xF4]
        self.pc = 0
        self.flag = False
        self.FL = 0b00000000
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE
        self.branchtable[AND] = self.handle_AND
        self.branchtable[OR] = self.handle_OR
        self.branchtable[XOR] = self.handle_XOR
        self.branchtable[NOT] = self.handle_NOT
        self.branchtable[SHL] = self.handle_SHL
        self.branchtable[SHR] = self.handle_SHR
        self.branchtable[MOD] = self.handle_MOD
        
    def load(self):
        """Load a program into memory."""
        address = 0
        if len(sys.argv) != 2:
            sys.exit('Please provide input in the format of "ls8.py [filname]"')

        with open(sys.argv[1]) as f:
            for line in f:
                instruction = re.match(r'\d{8}', line)
                if instruction is not None:
                    self.ram[address] = int(instruction.group(), 2)
                    address += 1
                else: 
                    continue

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'CMP':
            # reset CMP flag
            self.FL = 0b00000000
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b00000010
            else:
                self.FL = 0b00000100
        elif op == 'AND':
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == 'OR':
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == 'NOT':
            self.reg[reg_a] = ~ self.reg[reg_a]
        elif op == 'XOR':
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == 'SHL':
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == 'SHR':
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == 'MOD':
            if reg_b == 0:
                raise Exception('Cannot divide by 0')
            self.reg[reg_a] %= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_HLT(self, op_a, op_b):
        self.flag = False
        self.pc += 1

    def handle_LDI(self, op_a, op_b):
        self.raw_write(op_b, op_a)
        self.pc += 3

    def handle_PRN(self, op_a, op_b):
        print(self.reg[op_a])
        self.pc += 2
    
    def handle_MUL(self, op_a, op_b):
        self.alu('MUL', op_a, op_b)
        self.pc += 3
    
    def handle_ADD(self, op_a, op_b):
        self.alu('ADD', op_a, op_b)
        self.pc += 3

    def handle_PUSH(self, op_a, op_b):
        # Decrement SP
        # Copy value in register to address pointed to by SP
        self.reg[SP] -= 1  
        self.ram[self.reg[SP]] = self.reg[op_a]
        self.pc += 2 

    def handle_POP(self, op_a, op_b):
        # Copy value from address pointed to by SP to given register
        # Increment SP
        self.raw_write(self.ram[self.reg[SP]], op_a)
        self.reg[SP] += 1   
        self.pc += 2

    def handle_CALL(self, op_a, op_b):
        # Push the return address to the stack
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.pc + 2
        # Move PC to the address stored in the given register
        self.pc = self.reg[op_a]  

    def handle_RET(self, op_a, op_b):
        # Pop value from stack and store in the PC
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1 

    def handle_CMP(self, op_a, op_b):
        self.alu('CMP', op_a, op_b)
        self.pc += 3

    def handle_JMP(self, op_a, op_b):
        self.pc = self.reg[op_a]

    def handle_JNE(self, op_a, op_b):
        self.pc = self.reg[op_a] if self.FL != 0b00000001 else self.pc + 2
    
    def handle_JEQ(self, op_a, op_b):
        self.pc = self.reg[op_a] if self.FL == 0b00000001 else self.pc + 2

    def handle_AND(self, op_a, op_b):
        self.alu('AND', op_a, op_b)
        self.pc += 3
    
    def handle_OR(self, op_a, op_b):
        self.alu('OR', op_a, op_b)
        self.pc += 3

    def handle_XOR(self, op_a, op_b):
        self.alu('XOR', op_a, op_b)
        self.pc += 3

    def handle_NOT(self, op_a, op_b):
        self.alu('NOT', op_a, op_b)
        self.pc += 2

    def handle_SHL(self, op_a, op_b):
        self.alu('SHL', op_a, op_b)
        self.pc += 3

    def handle_SHR(self, op_a, op_b):
        self.alu('SHR', op_a, op_b)
        self.pc += 3
    
    def handle_MOD(self, op_a, op_b):
        self.alu('MOD', op_a, op_b)
        self.pc += 3

    def run(self):
        """Run the CPU."""
        self.flag = True

        while self.flag:
            ir = self.ram_read(self.pc)
            if ir in self.branchtable: 
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2) 
                self.branchtable[ir](operand_a, operand_b)
            else:
                print(f"Unknown instruction at index {self.pc}")
                self.flag = False
                self.trace()
                sys.exit(1)  

    def ram_read(self, address):
        return self.ram[address]

    def raw_write(self, value, address):
        self.reg[address] = value
