from __future__ import annotations

class BitReader:
    def __init__(self, data: bytes):
        self.data=data; self.pos=0; self.buf=0; self.bits=0
    def read_bits(self,n:int)->int:
        if n==0:return 0
        while self.bits<n:
            if self.pos>=len(self.data): raise EOFError
            self.buf=(self.buf<<8)|self.data[self.pos]; self.pos+=1; self.bits+=8
        shift=self.bits-n
        result=(self.buf>>shift)&((1<<n)-1)
        self.bits-=n
        self.buf &= (1<<self.bits)-1 if self.bits else 0
        return result
    def read_bit(self): return self.read_bits(1)

class Tree:
    LEAF=1<<15
    def __init__(self,size:int): self.data=[self.LEAF]*size
    def single(self,code:int): self.data[0]=code|self.LEAF
    def build(self,lengths:list[int],n:int):
        tree=self.data; tree_len=len(tree); next_entry=0; allocated=1; code_len=0
        while True:
            end=allocated
            new_nodes=(allocated-next_entry)*2
            if allocated+new_nodes<=tree_len:
                while next_entry<end:
                    tree[next_entry]=allocated; allocated+=2; next_entry+=1
            code_len+=1
            remaining=False
            for i in range(n):
                if lengths[i]==code_len:
                    if next_entry>=allocated: node=0
                    else: node=next_entry; next_entry+=1
                    tree[node]=i|self.LEAF
                elif lengths[i]>code_len: remaining=True
            if not remaining: break
    def read(self,br:BitReader)->int:
        code=self.data[0]
        while not (code & self.LEAF):
            bit=br.read_bit(); code=self.data[code+bit]
        return code & ~self.LEAF

class LH5:
    HISTORY_BITS=14; OFFSET_BITS=4; NUM_CODES=510; COPY_THRESHOLD=3
    MAX_TEMP_CODES=(1<<5)-1; MAX_OFFSET_CODES=(1<<4)-1
    def __init__(self,data:bytes):
        self.br=BitReader(data); self.ring=bytearray(b' '*(1<<14)); self.rpos=0; self.block=0
        self.temp=Tree(self.MAX_TEMP_CODES*2); self.code=Tree(self.NUM_CODES*2); self.offset=Tree(self.MAX_OFFSET_CODES*2)
    def read_length(self):
        n=self.br.read_bits(3)
        if n==7:
            while self.br.read_bit(): n+=1
        return n
    def read_temp(self):
        n=self.br.read_bits(5)
        if n==0: self.temp.single(self.br.read_bits(5)); return
        n=min(n,self.MAX_TEMP_CODES); lengths=[0]*self.MAX_TEMP_CODES; i=0
        while i<n:
            lengths[i]=self.read_length()
            if i==2:
                skip=self.br.read_bits(2)
                for _ in range(skip):
                    i+=1
                    if i<len(lengths): lengths[i]=0
            i+=1
        self.temp.build(lengths,n)
    def skip_count(self,code):
        if code==0:return 1
        if code==1:return self.br.read_bits(4)+3
        return self.br.read_bits(9)+20
    def read_code_table(self):
        n=self.br.read_bits(9)
        if n==0: self.code.single(self.br.read_bits(9)); return
        n=min(n,self.NUM_CODES); lengths=[0]*self.NUM_CODES; i=0
        while i<n:
            c=self.temp.read(self.br)
            if c<=2:
                for _ in range(self.skip_count(c)):
                    if i>=n: break
                    lengths[i]=0; i+=1
            else:
                lengths[i]=c-2; i+=1
        self.code.build(lengths,n)
    def read_offset_table(self):
        n=self.br.read_bits(self.OFFSET_BITS)
        if n==0: self.offset.single(self.br.read_bits(self.OFFSET_BITS)); return
        n=min(n,self.MAX_OFFSET_CODES); lengths=[0]*self.MAX_OFFSET_CODES
        for i in range(n): lengths[i]=self.read_length()
        self.offset.build(lengths,n)
    def new_block(self):
        self.block=self.br.read_bits(16); self.read_temp(); self.read_code_table(); self.read_offset_table()
    def read_offset(self):
        bits=self.offset.read(self.br)
        if bits==0:return 0
        if bits==1:return 1
        return self.br.read_bits(bits-1)+(1<<(bits-1))
    def output(self,b:int,out:bytearray):
        out.append(b); self.ring[self.rpos]=b; self.rpos=(self.rpos+1)&((1<<14)-1)
    def decompress(self,size:int)->bytes:
        out=bytearray()
        while len(out)<size:
            while self.block==0: self.new_block()
            self.block-=1
            c=self.code.read(self.br)
            if c<256: self.output(c,out)
            else:
                count=c-256+self.COPY_THRESHOLD
                off=self.read_offset(); start=self.rpos+(1<<14)-off-1
                for i in range(count):
                    self.output(self.ring[(start+i)&((1<<14)-1)],out)
                    if len(out)>=size: break
        return bytes(out)

def decompress(data:bytes,size:int)->bytes: return LH5(data).decompress(size)
