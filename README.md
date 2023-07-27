# quantum-arithmetic-operations

- Modular_Expo.py -
Input: a, x, N
Outuput: a^x mod N

The main codes are Composed of 6 regions.
1. Initilization
2. Appending or applying gates
3. Measure
4. Run
5. Export images

Note that the initilization of a, x, and N is restricted by come condtions.
1. the length of x and N in binary have to be equal to each other.
2. the production of a and x(n) is less than 2N
x(n) = 2 ^ (length(x) - 1)
length(x) = [log(x)] + 1

specification
when n = length(N) = length(x)
9n - 1 qubits needed in this circuit.
