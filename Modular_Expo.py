# region Imports
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute, Aer
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram, circuit_drawer
# endregion Imports

# region SUM
X = QuantumRegister(1, "in |X⟩")
Y = QuantumRegister(1, "in |Y⟩")
sum_out = QuantumRegister(1, "out SUM |0⟩")
SUM = QuantumCircuit(X, Y, sum_out, name='SUM')
SUM.cx(1, 2)
SUM.cx(0, 2)
SUM = SUM.to_instruction() 
# endregion SUM

# region carry
cin = QuantumRegister(1, 'in Carry')
cout = QuantumRegister(1, 'out Carry |0⟩')
carry = QuantumCircuit(cin,X,Y,cout,name="Carry")
carry.ccx(1,2,3)
carry.cx(1,2)
carry.ccx(0,2,3)
carry = carry.to_instruction()
# endregion carry

def ADD_for_Expo_Modulo(length2):

    Qa = QuantumRegister(length2, "in |A⟩")
    Qb = QuantumRegister(length2 + 1, "in |B⟩")
    Qc = QuantumRegister(length2, 'carry |0⟩')
    Qn = QuantumRegister(length2, 'N')

    Fadder = QuantumCircuit(Qa, Qb, Qc)

    for i in range(length2 - 1):
        Fadder.append(carry, [Qc[i], Qa[i], Qb[i], Qc[i + 1]])
    Fadder.append(carry, [Qc[length2 - 1], Qa[length2 - 1], Qb[length2 - 1], Qb[length2]])
    Fadder.cx(Qa[length2 - 1], Qb[length2 - 1])
    for j in range(length2 - 1, 0, -1):
        Fadder.append(SUM, [Qc[j], Qa[j], Qb[j]])
        Fadder.barrier()
        Fadder.append(carry.inverse(), [Qc[j - 1], Qa[j - 1], Qb[j - 1], Qc[j]])
    Fadder.append(SUM, [Qc[0], Qa[0], Qb[0]])

    # return Fadder.to_instruction()
    return Fadder

def Add_Modulo_for_Expo_Modulo(length2):

    Qxx = QuantumRegister(length2, "in |XX⟩")
    Qy = QuantumRegister(length2 + 1, "in |Y⟩")
    Qc = QuantumRegister(length2, 'carry |0⟩')
    Qn = QuantumRegister(length2, 'N')
    Qt = QuantumRegister(1, '0')

    circ = QuantumCircuit(Qxx, Qy, Qc, Qn, Qt)

    adder_modulo_instruction = ADD_for_Expo_Modulo(length2)

    circ.append(adder_modulo_instruction, Qxx[:] + Qy[:] + Qc[:])

    for i  in range(length2):
        circ.swap(Qxx[i],Qn[i])

    circ.append(adder_modulo_instruction.inverse(), Qxx[:] + Qy[:] + Qc[:])
    circ.barrier()

    circ.x(Qy[length2])
    circ.cx(Qy[length2],Qt[0])
    circ.x(Qy[length2])

    for i in range(length2):
        if bin(N)[-1 - i] == "1":
            circ.cx(Qt[0],Qxx[i])
    circ.barrier()

    circ.append(adder_modulo_instruction, Qxx[:] + Qy[:] + Qc[:])

    for i in range(length2):
        if bin(N)[-1 - i] == "1":
            circ.cx(Qt[0],Qxx[i])
    circ.barrier()

    for i  in range(length2):
        circ.swap(Qxx[i],Qn[i])

    circ.append(adder_modulo_instruction.inverse(), Qxx[:] + Qy[:] + Qc[:])

    circ.cx(Qy[length2],Qt[0])

    circ.append(adder_modulo_instruction, Qxx[:] + Qy[:] + Qc[:])

    return circ

def CMM_for_Expo_Modulo(length1, length2, a, x):
    # region Initialization ax < 2N, len(a) = len(x)

    Qctrl = QuantumRegister(1, "in |Ctrl⟩")
    Qx = QuantumRegister(length2 + 1, "in |X⟩")
    Qxx = QuantumRegister(length2, "in |XX⟩")

    Qy = QuantumRegister(length2 + 1, "in |Y⟩")

    Qc = QuantumRegister(length2, 'carry |0⟩')
    Qn = QuantumRegister(length2, 'N')
    Qt = QuantumRegister(1, '0')

    circ = QuantumCircuit(Qctrl, Qx, Qxx, Qy, Qc, Qn, Qt)

    adder_modulo_instruction = Add_Modulo_for_Expo_Modulo(length2)

    for i in range(length1):
        for j in range(len(bin(a)[2::])):
            if bin(a)[2:][j] == "1":
                circ.ccx(Qctrl[0],Qx[i],Qxx[i + j])
        circ.append(adder_modulo_instruction, Qxx[:] + Qy[:] + Qc[:] + Qn[:] + Qt[:])
        for j in range(len(bin(a)[2::])):
            if bin(a)[2:][j] == "1":
                circ.ccx(Qctrl[0],Qx[i],Qxx[i + j])
    circ.barrier()

    circ.x(Qctrl[0])
    for i in range(length2):
        circ.ccx(Qctrl[0],Qx[i],Qy[i])
    circ.x(Qctrl[0])
    circ.barrier()

    return circ

#region Initialization length(x) = length(N), a*xn < 2N (xn = 2 ^ (length(x) - 1))
a = 1
x = 1
N = 1

length1 = len(bin(N)[2:])
length2 = min((length1 + len(bin(a)), 2 * length1 -1))

Qx = QuantumRegister(length1, "in |X⟩")
Qctrl = QuantumRegister(1, "|Ctrl⟩")
Qr = QuantumRegister(length2 + 1, "|Result⟩")
Qtemp_expo = QuantumRegister(length2 + 1, "|temp1⟩")

Qtemp_cmm = QuantumRegister(length2, "|temp2⟩")

Qc = QuantumRegister(length2, 'carry |0⟩')
Qn = QuantumRegister(length2, 'N')
Qt = QuantumRegister(1, '0')
Cc = ClassicalRegister(length1, "Result")

circ = QuantumCircuit(Qx, Qctrl, Qr, Qtemp_expo, Qtemp_cmm, Qc, Qn, Qt, Cc)

length1 = len(bin(N)[2:])
length2 = min(len(bin(a)[2:]) + length1, 2 * length1 - 1)

for i in range(length1):
    circ.initialize(Statevector.from_label(bin(x)[2:].zfill(length1)[::-1][i]), Qx[i])
circ.initialize([1, 0], Qctrl[0])

for i in range(length2 + 1):
    circ.initialize(Statevector.from_label(bin(1)[2:].zfill(length2 + 1)[::-1][i]), Qr[i])
    circ.initialize([1, 0], Qtemp_expo[i])

for i in range(length2):
    circ.initialize([1, 0], Qtemp_cmm[i])
    circ.initialize([1, 0], Qc[i])
    circ.initialize(Statevector.from_label(bin(N)[2:].zfill(length2)[::-1][i]), Qn[i])
circ.initialize([1, 0], Qt[0])

#endregion Initialization

#region Appending or applying gates

CCM_instruction = CMM_for_Expo_Modulo(length1, length2, a, x)

for i in range(length1):
# for i in range(length1):
    circ.cx(Qx[i],Qctrl[0])
    for ii in range(i + 1):
        circ.append(CCM_instruction, Qctrl[:] + Qr[:] + Qtemp_cmm[:] + Qtemp_expo[:] + Qc[:] + Qn[:] + Qt[:])
        for k in range(length2 + 1):
            circ.swap(Qr[k], Qtemp_expo[k])
        circ.append(CCM_instruction.inverse(), Qctrl[:] + Qr[:] + Qtemp_cmm[:] + Qtemp_expo[:] + Qc[:] + Qn[:] + Qt[:])
    circ.cx(Qx[i],Qctrl[0])
    circ.barrier()

#endregion Appending or applying gates

# region Measure
for i in range(length1):
    circ.measure(Qr[i], Cc[i])
# endregion Measure

# region Run

backend = Aer.get_backend('qasm_simulator')
result = execute(circ, backend, shots=1).result()
counts = result.get_counts()
print(counts)

# endregion Run

# region Export images
circ.draw(output='mpl', filename='Expo_Modulo_diagram.png')
# endregion Export images