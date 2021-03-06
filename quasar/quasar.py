# Quasar: an ultralight python-2.7/python-3.X quantum simulator package
# Copyright (C) 2019 Robert Parrish
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# 
# Contact:
# Robert Parrish
# robparrish@gmail.com

import numpy as np
import collections

""" Quasar: an ultralight python-2.7/python-3.X quantum simulator package

Note on Qubit Order:

We use the standard QIS qubit order of Nielsen and Chuang, where the qubits are
ordered from left to right in the ket, i.e., |0123>. For instance, the circuit:

T   : |0|
         
|0> : -H-
         
|1> : ---
         
|2> : ---
         
|3> : ---

T   : |0|

Produces the state (|0000> + |1000>) / sqrt(2), which appears in the simulated
state vector as:

[0.70710678 0.         0.         0.         0.         0.
 0.         0.         0.70710678 0.         0.         0.
 0.         0.         0.         0.        ]

E.g., the 0-th (|0000>) and 8-th (|1000>) coefficient are set.

This ordering is used in many places in QIS, e.g., Cirq, but the opposite
ordering is also sometimes seen, e.g., in Qiskit.
"""

# => Matrix class <= #

class Matrix(object):

    """ Class Matrix holds several common matrices encountered in quantum circuits.

    These matrices are stored in np.ndarray with dtype=np.complex128.

    The naming/ordering of the matrices in Quasar follows that of Nielsen and
    Chuang, *except* that rotation matrices are specfied in full turns:

        Rz(theta) = exp(-i*theta*Z)
    
    whereas Nielsen and Chuang define these in half turns:

        Rz^NC(theta) = exp(-i*theta*Z/2)
    """

    I = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.complex128)
    X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
    Y = np.array([[0.0, -1.0j], [+1.0j, 0.0]], dtype=np.complex128)
    Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
    S = np.array([[1.0, 0.0], [0.0, 1.0j]], dtype=np.complex128)
    T = np.array([[1.0, 0.0], [0.0, np.exp(np.pi/4.0*1.j)]], dtype=np.complex128)
    H = 1.0 / np.sqrt(2.0) * np.array([[1.0, 1.0], [1.0, -1.0]], dtype=np.complex128)
    # exp(+i (pi/4) * X) : Z -> Y basis transformation
    Rx2 = 1.0 / np.sqrt(2.0) * np.array([[1.0, +1.0j], [+1.0j, 1.0]], dtype=np.complex128)
    Rx2T = 1.0 / np.sqrt(2.0) * np.array([[1.0, -1.0j], [-1.0j, 1.0]], dtype=np.complex128)

    II = np.kron(I, I)
    IX = np.kron(I, X)
    IY = np.kron(I, Y)
    IZ = np.kron(I, Z)
    XI = np.kron(X, I)
    XX = np.kron(X, X)
    XY = np.kron(X, Y)
    XZ = np.kron(X, Z)
    YI = np.kron(Y, I)
    YX = np.kron(Y, X)
    YY = np.kron(Y, Y)
    YZ = np.kron(Y, Z)
    ZI = np.kron(Z, I)
    ZX = np.kron(Z, X)
    ZY = np.kron(Z, Y)
    ZZ = np.kron(Z, Z)

    CX = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0, 0.0],
        ], dtype=np.complex128)
    CNOT = CX
    CY = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, -1.0j],
        [0.0, 0.0, +1.0j, 0.0],
        ], dtype=np.complex128)
    CZ = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, -1.0],
        ], dtype=np.complex128)
    CS = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0j],
        ], dtype=np.complex128)
    SWAP = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        ], dtype=np.complex128)

    @staticmethod
    def Rx(theta):
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([[c, -1.j*s], [-1.j*s, c]], dtype=np.complex128)

    @staticmethod
    def Ry(theta):
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([[c, -s], [+s, c]], dtype=np.complex128)

    @staticmethod
    def Rz(theta):
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([[c-1.j*s, 0.0], [0.0, c+1.j*s]], dtype=np.complex128)
    
# => Gate class <= #

class Gate(object):

    """ Class Gate represents a general N-body quantum gate. 

    An N-body quantum gate applies a unitary operator to the state of a subset
    of N qubits, with an implicit identity matrix acting on the remaining
    qubits. The Gate class specifies the (2**N,)*2 unitary matrix U for the N
    active qubits, but does not specify which qubits are active.

    Usually, most users will not initialize their own Gates, but will use gates
    from the standard library, which are defined as Gate class members (for
    parameter-free gates) or Gate class methods (for parameter-including gates).
    Some simple examples include:

    >>> I = Gate.I
    >>> Ry = Gate.Ry(theta=np.pi/4.0)
    >>> SO4 = Gate.SO4(A=0.0, B=0.0, C=0.0, D=0.0, E=0.0, F=0.0)
    >>> CF = Gate.CF(theta=np.pi/3.0)
    """

    def __init__(
        self,
        N,
        Ufun,
        params,
        name,
        ascii_symbols,
        ):

        """ Initializer. Params are set as object attributes.

        Params:
            N (int > 0) - the dimensionality of the quantum gate, e.g, 1 for
                1-body, 2 for 2-body, etc.
            Ufun (function of OrderedDict of str : float -> np.ndarray of shape
                (2**N,)*2) - a function which generates the unitary
                matrix for this gate from the current parameter set.
            params (OrderedDict of str : float) - the dictionary of initial
                gate parameters.
            name (str) - a simple name for the gate, e.g., 'CNOT'
            ascii_symbols (list of str of len N) - a list of ASCII symbols for
                each active qubit of the gate, for use in generating textual diagrams, e.g.,
                ['@', 'X'] for CNOT.
        """
        
        self.N = N
        self.Ufun = Ufun
        self.params = params
        self.name = name
        self.ascii_symbols = ascii_symbols

        # Validity checks
        if not isinstance(self.N, int): raise RuntimeError('N must be int')
        if self.N <= 0: raise RuntimeError('N <= 0') 
        if self.U.shape != (2**self.N,)*2: raise RuntimeError('U must be shape (2**N,)*2')
        if not isinstance(self.params, collections.OrderedDict): raise RuntimeError('params must be collections.OrderedDict')
        if not all(isinstance(_, str) for _ in list(self.params.keys())): raise RuntimeError('params keys must all be str')
        if not all(isinstance(_, float) for _ in list(self.params.values())): raise RuntimeError('params values must all be float')
        if not isinstance(self.name, str): raise RuntimeError('name must be str')
        if not isinstance(self.ascii_symbols, list): raise RuntimeError('ascii_symbols must be list')
        if len(self.ascii_symbols) != self.N: raise RuntimeError('len(ascii_symbols) != N')
        if not all(isinstance(_, str) for _ in self.ascii_symbols): raise RuntimeError('ascii_symbols must all be str')

    def __str__(self):
        """ String representation of this Gate (self.name) """
        return self.name
    
    @property
    def U(self): 
        """ The (2**N,)*2 unitary matrix underlying this Gate. 

        The action of the gate on a given state is given graphically as,

        |\Psi> -G- |\Psi'>

        and mathematically as,

        |\Psi_I'> = \sum_J U_IJ |\Psi_J>

        Returns:
            (np.ndarray of shape (2**N,)*2) - the unitary matrix underlying
                this gate, built from the current parameter state.
        """
        return self.Ufun(self.params)

    # > Copying < #
    
    def copy(self):
        """ Make a deep copy of the current Gate. 
        
        Returns:
            (Gate) - a copy of this Gate whose parameters may be modified
                without modifying the parameters of self.
        """
        return Gate(
            N=self.N, 
            Ufun=self.Ufun, 
            params=self.params.copy(), 
            name=self.name,  
            ascii_symbols=self.ascii_symbols,
            )

    # > Parameter Access < #

    def set_param(self, key, param):
        """ Set the value of a parameter of this Gate. 

        Params:
            key (str) - the key of the parameter
            param (float) - the value of the parameter
        Result:
            self.params[key] = param. If the Gate does not have a parameter
                corresponding to key, a RuntimeError is thrown.
        """
        if key not in self.params: raise RuntimeError('Key %s is not in params' % key)
        self.params[key] = param

    def set_params(self, params):
        """ Set the values of multiple parameters of this Gate.

        Params:
            params (dict of str : float) -  dict of param values
        Result:
            self.params is updated with the contents of params by calling
                self.set_param for each key/value pair.
        """
        for key, param in params.items():
            self.set_param(key=key, param=param)

# > Explicit 1-body gates < #

""" I (identity) gate """
Gate.I = Gate(
    N=1,
    Ufun = lambda params : Matrix.I,
    params=collections.OrderedDict(),
    name='I',
    ascii_symbols=['I'],
    )
""" X (NOT) gate """
Gate.X = Gate(
    N=1,
    Ufun = lambda params : Matrix.X,
    params=collections.OrderedDict(),
    name='X',
    ascii_symbols=['X'],
    )
""" Y gate """
Gate.Y = Gate(
    N=1,
    Ufun = lambda params : Matrix.Y,
    params=collections.OrderedDict(),
    name='Y',
    ascii_symbols=['Y'],
    )
""" Z gate """
Gate.Z = Gate(
    N=1,
    Ufun = lambda params : Matrix.Z,
    params=collections.OrderedDict(),
    name='Z',
    ascii_symbols=['Z'],
    )
""" H (Hadamard) gate """
Gate.H = Gate(
    N=1,
    Ufun = lambda params : Matrix.H,
    params=collections.OrderedDict(),
    name='H',
    ascii_symbols=['H'],
    )
""" S gate """
Gate.S = Gate(
    N=1,
    Ufun = lambda params : Matrix.S,
    params=collections.OrderedDict(),
    name='S',
    ascii_symbols=['S'],
    )
""" T gate """
Gate.T = Gate(
    N=1,
    Ufun = lambda params : Matrix.T,
    name='T',
    params=collections.OrderedDict(),
    ascii_symbols=['T'],
    )
""" Rx2 gate """
Gate.Rx2 = Gate(
    N=1,
    Ufun = lambda params : Matrix.Rx2,
    params=collections.OrderedDict(),
    name='Rx2',
    ascii_symbols=['Rx2'],
    )
""" Rx2T gate """
Gate.Rx2T = Gate(
    N=1,
    Ufun = lambda params : Matrix.Rx2T,
    params=collections.OrderedDict(),
    name='Rx2T',
    ascii_symbols=['Rx2T'],
    )

# > Explicit 2-body gates < #

""" CNOT (CX) gate """
Gate.CNOT = Gate(
    N=2,
    Ufun = lambda params: Matrix.CX,
    params=collections.OrderedDict(),
    name='CNOT',
    ascii_symbols=['@', 'X'],
    )
Gate.CX = Gate.CNOT # Common alias
""" CY gate """
Gate.CY = Gate(
    N=2,
    Ufun = lambda params: Matrix.CY,
    params=collections.OrderedDict(),
    name='CY',
    ascii_symbols=['@', 'Y'],
    )
""" CZ gate """
Gate.CZ = Gate(
    N=2,
    Ufun = lambda params: Matrix.CZ,
    params=collections.OrderedDict(),
    name='CZ',
    ascii_symbols=['@', 'Z'],
    )
""" CS gate """
Gate.CS = Gate(
    N=2,
    Ufun = lambda params: Matrix.CS,
    params=collections.OrderedDict(),
    name='CS',
    ascii_symbols=['@', 'S'],
    )
""" SWAP gate """
Gate.SWAP = Gate(
    N=2,
    Ufun = lambda params: Matrix.SWAP,
    params=collections.OrderedDict(),
    name='SWAP',
    ascii_symbols=['X', 'X'],
    )

# > Parametrized 1-body gates < #

@staticmethod
def _GateRx(theta):

    """ Rx (theta) = exp(-i * theta * x) """
    
    def Ufun(params):
        theta = params['theta']
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([[c, -1.j*s], [-1.j*s, c]], dtype=np.complex128)
    
    return Gate(
        N=1,
        Ufun=Ufun,
        params=collections.OrderedDict([('theta', theta)]),
        name='Rx',
        ascii_symbols=['Rx'],
        )
    
@staticmethod
def _GateRy(theta):

    """ Ry (theta) = exp(-i * theta * Y) """
    
    def Ufun(params):
        theta = params['theta']
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([[c, -s], [+s, c]], dtype=np.complex128)

    return Gate(
        N=1,
        Ufun=Ufun,
        params=collections.OrderedDict([('theta', theta)]),
        name='Ry',
        ascii_symbols=['Ry'],
        )
    
@staticmethod
def _GateRz(theta):

    """ Rz (theta) = exp(-i * theta * Z) """
    
    def Ufun(params):
        theta = params['theta']
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([[c-1.j*s, 0.0], [0.0, c+1.j*s]], dtype=np.complex128)

    return Gate(
        N=1,
        Ufun=Ufun,
        params=collections.OrderedDict([('theta', theta)]),
        name='Rz',
        ascii_symbols=['Rz'],
        )
    
Gate.Rx = _GateRx
Gate.Ry = _GateRy
Gate.Rz = _GateRz

# > Parametrized 2-body gates < #

@staticmethod
def _GateSO4(A, B, C, D, E, F):
    
    def Ufun(params):
        A = params['A']
        B = params['B']
        C = params['C']
        D = params['D']
        E = params['E']
        F = params['F']
        X = np.array([
            [0.0, +A,  +B,  +C],
            [-A, 0.0,  +D,  +E],
            [-B,  -D, 0.0,  +F],
            [-C,  -E,  -F, 0.0],
            ])
        import scipy.linalg
        U = scipy.linalg.expm(X)
        return np.array(U, dtype=np.complex128)

    return Gate(
        N=2,
        Ufun=Ufun,
        params=collections.OrderedDict([('A', A), ('B', B), ('C', C), ('D', D), ('E', E), ('F', F)]),
        name='SO4',
        ascii_symbols=['SO4A', 'SO4B'],
        )

Gate.SO4 = _GateSO4

@staticmethod
def _GateSO42(thetaIY, thetaYI, thetaXY, thetaYX, thetaZY, thetaYZ):
    
    def Ufun(params):
        A = -(params['thetaIY'] + params['thetaZY'])
        F = -(params['thetaIY'] - params['thetaZY'])
        C = -(params['thetaYX'] + params['thetaXY'])
        D = -(params['thetaYX'] - params['thetaXY'])
        B = -(params['thetaYI'] + params['thetaYZ'])
        E = -(params['thetaYI'] - params['thetaYZ'])
        X = np.array([
            [0.0, +A,  +B,  +C],
            [-A, 0.0,  +D,  +E],
            [-B,  -D, 0.0,  +F],
            [-C,  -E,  -F, 0.0],
            ])
        import scipy.linalg
        U = scipy.linalg.expm(X)
        return np.array(U, dtype=np.complex128)

    return Gate(
        N=2,
        Ufun=Ufun,
        params=collections.OrderedDict([
            ('thetaIY' , thetaIY),
            ('thetaYI' , thetaYI),
            ('thetaXY' , thetaXY),
            ('thetaYX' , thetaYX),
            ('thetaZY' , thetaZY),
            ('thetaYZ' , thetaYZ),
        ]),
        name='SO42',
        ascii_symbols=['SO42A', 'SO42B'],
        )

Gate.SO42 = _GateSO42

@staticmethod
def _CF(theta):

    """ Controlled F gate """
    
    def Ufun(params):
        theta = params['theta']
        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0,  +c,  +s],
            [0.0, 0.0,  +s,  -c],
            ], dtype=np.complex128)
    
    return Gate(
        N=2,
        Ufun=Ufun,
        params=collections.OrderedDict([('theta', theta)]),
        name='CF',
        ascii_symbols=['@', 'F'],
        )

Gate.CF = _CF

# > Special explicit gates < #

@staticmethod
def _GateU1(U):

    """ An explicit 1-body gate that is specified by the user. """

    return Gate(
        N=1,
        Ufun = lambda params : U,
        params=collections.OrderedDict(),
        name='U1',
        ascii_symbols=['U1'],
        )

@staticmethod
def _GateU2(U):

    """ An explicit 2-body gate that is specified by the user. """

    return Gate(
        N=2,
        Ufun = lambda params : U,
        params=collections.OrderedDict(),
        name='U2',
        ascii_symbols=['U2A', 'U2B'],
        )

Gate.U1 = _GateU1
Gate.U2 = _GateU2

# => Gate class <= #

class Circuit(object):

    """ Class Circuit represents a general quantum circuit acting on N
        linearly-arranged cubits. Non-local connectivity is permitted - the
        linear arrangement is strictly for simplicity.

        An example Circuit construction is,

        >>> circuit = Circuit(N=2)
        >>> circuit.add_gate(T=0, key=0, Gate.H)
        >>> circuit.add_gate(T=0, key=(1,), Gate.X)
        >>> circuit.add_gate(T=1, key=(0,1), Gate.CNOT)
        >>> print(circuit)
        
        A Circuit is always constructed with a fixed number of qubits N, but
        the time window of the circuit is freely expandable from T=0 onward.
        The Circuit starts empty, and is filled one gate at a time by the
        add_gate function.
    
        The Circuit attribute Ts (list of int) contains the sorted list of time
        indices T with significant gates, and the Circuit attribute nmoment
        (int) contains the total number of time moments, including empty
        moments.

        The core data of a Circuit is the gates attribute, which contains an
        OrderedDict of (T, key) : Gate pairs for significant gates. The (T, key)
        compound key specifies the time moment of the gate T (int), and the qubit
        connections in key (tuple of int). len(key) is always gate.N.
        """

    def __init__(
        self,
        N,
        ):

        """ Initializer.

        Params:
            N (int) - number of qubits in this circuit
        """

        self.N = N
        # All circuits must have at least one qubit
        if self.N <= 0: raise RuntimeError('N <= 0')
    
        # Primary circuit data structure
        self.gates = collections.OrderedDict() # (T, (A, [B], [C], ...)) -> Gate
        # Memoization
        self.Ts = [] # [T] tells ordered, unique time moments
        self.TAs = set() # ({T,A}) tells occupied circuit indices

    # > Simple Circuit characteristics < #

    @property
    def nmoment(self):
        """ The total number of time moments in the circuit (including blank moments) """
        return self.Ts[-1] + 1 if len(self.Ts) else 0

    @property
    def ngate(self):
        """ The total number of gates in the circuit. """
        return len(self.gates)

    @property
    def ngate1(self):
        """ The total number of 1-body gates in the circuit. """
        return len([gate for gate in list(self.gates.values()) if gate.N == 1])

    @property
    def ngate2(self):
        """ The total number of 2-body gates in the circuit. """
        return len([gate for gate in list(self.gates.values()) if gate.N == 2])

    # > Gate addition < #

    def add_gate(
        self,
        T,
        key,
        gate,
        ):

        """ Add a gate to the circuit.

        Params:
            T (int) - the time index to add the gate at
            key (int or tuple of int) - the qubit index or indices to add the gate at
            gate (Gate) - the gate to add 
        Result:
            self is updated with the added gate. Checks are performed to ensure
                that the addition is valid.

        For one body gate, can add as either of:
            circuit.add_gate(T, A, gate)
            circuit.add_gate(T, (A,), gate)
        For two body gate, must add as:
            circuit.add_gate(T, (A, B), gate)
        """

        # Make key a tuple regardless of input
        key2 = (key,) if isinstance(key, int) else key
        # Check that T >= 0
        if T < 0: raise RuntimeError('Negative T: %d' % T)
        # Check that key makes sense for gate.N
        if len(key2) != gate.N: raise RuntimeError('%d key entries provided for %d-body gate' % (len(key2), gate.N))
        # Check that the requested circuit locations are open
        for A in key2:
            if (T,A) in self.TAs: 
                raise RuntimeError('T=%d, A=%d circuit location is already occupied' % (T,A))
            if A >= self.N:
                raise RuntimeError('No qubit location %d' % A)
        # Add gate to circuit
        self.gates[(T, key2)] = gate
        # Update memoization of TAs and Ts
        for A in key2:
            self.TAs.add((T,A))
        if T not in self.Ts:
            self.Ts = list(sorted(self.Ts + [T]))

    def gate(
        self,
        T,
        key,
        ):

        """ Return the gate at a given moment T and qubit indices key

        Params:
            T (int) - the time index of the gate
            key (int or tuple of int) - the qubit index or indices of the gate
        Returns:
            (Gate) - the gate at the specified circuit coordinates

        For one body gate, can use as either of:
            gate = circuit.gate(T, A)
            gate = circuit.gate(T, (A,))
        For two body gate, must use as:
            gate = circuit.gate(T, (A, B))
        """

        # Make key a tuple regardless of input
        key2 = (key,) if isinstance(key, int) else key
        return self.gates[(T, key2)]

    # => Copy/Subsets/Concatenation <= #

    def copy(
        self,
        ):

        """ Return a copy of circuit self so that parameter modifications in
            the copy do not affect self.

        Returns:
            (Circuit) - copy of self with all Gate objects copied deeply enough
                to remove parameter dependencies between self and returned
                Circuit.
        """

        circuit = Circuit(N=self.N)
        for key, gate in self.gates.items():
            T, key2 = key
            circuit.add_gate(T=T, key=key2, gate=gate.copy())
        return circuit

    def subset(
        self,
        Ts,
        copy=True,
        ):

        """ Return a Circuit with a subset of time moments Ts.

        Params:
            Ts (list of int) - ordered time moments to slice into time moments
                [0,1,2,...] in the returned circuit.
            copy (bool) - copy Gate elements to remove parameter dependencies
                between self and returned circuit (True - default) or not
                (False). 
        Returns:
            (Circuit) - the time-sliced circuit.
        """

        circuit = Circuit(N=self.N)
        for T2, Tref in enumerate(Ts):
            if Tref >= self.nmoment: raise RuntimeError('T >= self.nmoment: %d' % Tref)
        for key, gate in self.gates.items():
            T, key2 = key
            if T in Ts:
                T2 = [T2 for T2, Tref in enumerate(Ts) if Tref == T][0]
                circuit.add_gate(T=T2, key=key2, gate=gate.copy() if copy else gate)
        return circuit

    @staticmethod
    def concatenate(
        circuits,
        copy=True,
        ):

        """ Concatenate a list of Circuits in time.
        
        Params:
            circuits (list of Circuit) - the ordered list of Circuit objects to
                concatenate in time.
            copy (bool) - copy Gate elements to remove parameter dependencies
                between circuits and returned circuit (True - default) or not
                (False). 
        Returns:
            (Circuit) - the time-concatenated circuit.
        """

        if any(x.N != circuits[0].N for x in circuits): 
            raise RuntimeError('Circuits must all have same N to be concatenated')
        
        circuit = Circuit(N=circuits[0].N)
        Tstart = 0
        for circuit2 in circuits:   
            for key, gate in circuit2.gates.items():
                T, key2 = key
                circuit.add_gate(T=T+Tstart, key=key2, gate=gate.copy() if copy else gate)
            Tstart += circuit2.nmoment
        return circuit

    def deadjoin(
        self,
        keys,
        copy=True,
        ):

        """ Return a circuit with a subset of spatial qubit keys.

        Params:
            keys (list of int) - ordered qubit indices to slice in spatial
                indices into the [0,1,2...] indices in the returned circuit.
            copy (bool) - copy Gate elements to remove parameter dependencies
                between self and returned circuit (True - default) or not
                (False). 
        Returns:
            (Circuit) - the qubit-sliced circuit.
        """

        for A2, Aref in enumerate(keys):
            if Aref >= self.N: raise RuntimeError('A >= self.A: %d' % Aref)

        Amap = { v : k for k, v in enumerate(keys) }

        circuit = Circuit(N=len(keys))
        for key, gate in self.gates.items():
            T, key2 = key
            if all(x in Amap for x in key2):
                circuit.add_gate(T=T, key=tuple(Amap[x] for x in key2), gate=gate.copy() if copy else gate)
        return circuit

    @staticmethod
    def adjoin(
        circuits,
        copy=True,
        ):

        """ Adjoin a list of Circuits in spatial qubit indices.
        
        Params:
            circuits (list of Circuit) - the ordered list of Circuit objects to
                adjoin in spatial qubit indices.
            copy (bool) - copy Gate elements to remove parameter dependencies
                between circuits and returned circuit (True - default) or not
                (False). 
        Returns:
            (Circuit) - the spatially qubit-adjoined circuit.
        """
        circuit = Circuit(N=sum(x.N for x in circuits))
        Astart = 0
        for circuit2 in circuits:   
            for key, gate in circuit2.gates.items():
                T, key2 = key
                circuit.add_gate(T=T, key=tuple(x + Astart for x in key2), gate=gate.copy() if copy else gate)
            Astart += circuit2.N
        return circuit
    
    def reversed(
        self,
        copy=True,
        ):

        """ Return a circuit with gate operations in reversed time order.

        Note that the gates are not transposed/adjointed => this is not
            generally equivalent to time reversal.

        Params:
            copy (bool) - copy Gate elements to remove parameter dependencies
                between self and returned circuit (True - default) or not
                (False). 
        Returns:
            (Circuit) - the reversed circuit.
        """

        circuit = Circuit(N=self.N)
        for key, gate in self.gates.items():
            T, key2 = key
            circuit.add_gate(T=self.nmoment-T-1, key=key2, gate=gate)
        return circuit

    def nonredundant(
        self,
        copy=True,
        ):

        """ Return a circuit with empty time moments removed.

        Params:
            copy (bool) - copy Gate elements to remove parameter dependencies
                between self and returned circuit (True - default) or not
                (False). 
        Returns:
            (Circuit) - the time-dense circuit.
        """

        circuit = Circuit(N=self.N)
        Tmap = { v : k for k, v in enumerate(sorted(self.Ts)) }
        for key, gate in self.gates.items():
            T, key2 = key
            circuit.add_gate(T=Tmap[T], key=key2, gate=gate)
        return circuit

    def compressed(
        self,
        ):

        """ Return an equivalent time-dense circuit with 1- and 2-body gates
            merged together to minimize the number of gates by using composite
            1- and 2-body gate operations. This operation is designed to reduct
            the runtime of state vector simulation by reducing the number of 1-
            and 2-body gate operations that must be simulated.

        This operation freezes the current parameter values of all gates, and
        constructs composite 1- and 2-body gates from the current values of the gate
        unitary matrices U. Therefore, the returned circuit will have no
        parameters, and compressed will have to be called on the original
        circuit again if the parameters change.

        Returns:
            (Circuit) - the compressed circuit.
        """

        # Jam consecutive 1-body gates (removes runs of 1-body gates)
        circuit1 = self.copy()
        plan = [[0 for x in range(self.nmoment)] for y in range(self.N)]
        for key, gate in circuit1.gates.items():
            T, key2 = key
            if gate.N == 1:
                A, = key2
                plan[A][T] = 1
            elif gate.N == 2:
                A, B = key2
                plan[A][T] = 2
                plan[B][T] = -2
            else:
                raise RuntimeError("N > 2")
        circuit2 = Circuit(N=self.N)
        for A, row in enumerate(plan):
            Tstar = None
            U = None
            for T, V in enumerate(row):
                # Start the 1-body gate chain
                if V == 1 and U is None:
                    Tstar = T
                    U = np.copy(circuit1.gates[T,(A,)].U)
                # Continue the 1-body gate chain
                elif V == 1:
                    U = np.dot(circuit1.gates[T,(A,)].U, U)
                # If 2-body gate or end of circuit encountered, place 1-body gate
                if U is not None and (V == 2 or V == -2 or T == self.nmoment - 1):
                    circuit2.add_gate(T=Tstar, key=(A,), gate=Gate.U1(U=U))
                    Tstar = None
                    U = None
        for key, gate in circuit1.gates.items():
            T, key2 = key
            if gate.N == 2:
                circuit2.add_gate(T=T, key=key2, gate=gate)

        # Jam 1-body gates into 2-body gates if possible (not possible if 1-body gate wire)
        circuit1 = circuit2
        plan = [[0 for x in range(self.nmoment)] for y in range(self.N)]
        for key, gate in circuit1.gates.items():
            T, key2 = key
            if gate.N == 1:
                A, = key2
                plan[A][T] = 1
            elif gate.N == 2:
                A, B = key2
                plan[A][T] = 2
                plan[B][T] = -2
            else:
                raise RuntimeError("N > 2")
        circuit2 = Circuit(N=self.N)
        jammed_gates = {}                 
        for key, gate in circuit1.gates.items():
            if gate.N != 2: continue
            T, key2 = key
            A, B = key2
            U = np.copy(gate.U)
            # Left-side 1-body gates
            for T2 in range(T-1,-1,-1):
                if plan[A][T2] == 2 or plan[A][T2] == -2: break
                if plan[A][T2] == 1:
                    gate1 = circuit1.gates[T2, (A,)]
                    U = np.dot(U, np.kron(gate1.U, np.eye(2)))
                    jammed_gates[T2, (A,)] = gate1
                    break
            for T2 in range(T-1,-1,-1):
                if plan[B][T2] == 2 or plan[B][T2] == -2: break
                if plan[B][T2] == 1:
                    gate1 = circuit1.gates[T2, (B,)]
                    U = np.dot(U, np.kron(np.eye(2), gate1.U))
                    jammed_gates[T2, (B,)] = gate1
                    break
            # Right-side 1-body gates (at circuit end)
            if T+1 < self.nmoment and max(abs(plan[A][T2]) for T2 in range(T+1, self.nmoment)) == 1:
                T2 = [T3 for T3, P in enumerate(plan[A][T+1:self.nmoment]) if P == 1][0] + T+1
                gate1 = circuit1.gates[T2, (A,)]
                U = np.dot(np.kron(gate1.U, np.eye(2)), U)
                jammed_gates[T2, (A,)] = gate1
            if T+1 < self.nmoment and max(abs(plan[B][T2]) for T2 in range(T+1, self.nmoment)) == 1:
                T2 = [T3 for T3, P in enumerate(plan[B][T+1:self.nmoment]) if P == 1][0] + T+1
                gate1 = circuit1.gates[T2, (B,)]
                U = np.dot(np.kron(np.eye(2), gate1.U), U)
                jammed_gates[T2, (B,)] = gate1
            circuit2.add_gate(T=T, key=key2, gate=Gate.U2(U=U))
        # Unjammed gates (should all be 1-body on 1-body wires) 
        for key, gate in circuit1.gates.items():
            if gate.N != 1: continue
            T, key2 = key
            if key not in jammed_gates:
                circuit2.add_gate(T=T, key=key2, gate=gate)

        # Jam 2-body gates, if possible
        circuit1 = circuit2
        circuit2 = Circuit(N=self.N)
        jammed_gates = {}
        for T in range(circuit1.nmoment):
            circuit3 = circuit1.subset([T])
            for key, gate in circuit3.gates.items():
                if gate.N != 2: continue
                T4, key2 = key
                if (T, key2) in jammed_gates: continue
                A, B = key2
                jams = [((T, key2), gate, False)]
                for T2 in range(T+1, self.nmoment):
                    if (T2, (A, B)) in circuit1.gates:
                        jams.append(((T2, (A, B)), circuit1.gates[(T2, (A, B))], False))
                    elif (T2, (B, A)) in circuit1.gates:
                        jams.append(((T2, (B, A)), circuit1.gates[(T2, (B, A))], True))
                    elif (T2, A) in circuit1.TAs:
                        break # Interference
                    elif (T2, B) in circuit1.TAs:
                        break # Interference
                U = np.copy(jams[0][1].U)
                for idx in range(1, len(jams)):
                    key, gate, trans = jams[idx]
                    U2 = np.copy(gate.U)
                    if trans:
                        U2 = np.reshape(np.einsum('ijkl->jilk', np.reshape(U2, (2,)*4)), (4,)*2)
                    U = np.dot(U2,U)
                circuit2.add_gate(T=T, key=(A,B), gate=Gate.U2(U=U))
                for key, gate, trans in jams:
                    jammed_gates[key] = gate
        # Unjammed gates (should all be 1-body on 1-body wires)
        for key, gate in circuit1.gates.items():
            if gate.N != 1: continue
            T, key2 = key
            if key not in jammed_gates:
                circuit2.add_gate(T=T, key=key2, gate=gate)

        return circuit2.nonredundant()

    # > Parameter Access/Manipulation < #

    @property
    def nparam(self):
        """ The total number of mutable parameters in the circuit. """
        return len(self.param_keys)

    @property
    def param_keys(self):
        """ A list of (T, key, param_name) for all mutable parameters in the circuit.

        A global order of (T, key, param_name within gate) is used to guarantee
        a stable, lexical ordering of circuit parameters for a given circuit.

        Returns:
            list of (int, tuple of int, str)) - ordered T moments, qubit
                indices, and gate parameter names for all mutable parameters in
                the circuit.
        """
        keys = []
        for key, gate in self.gates.items():
            T, key2 = key
            for name, v in gate.params.items():
                keys.append((T, key2, name))
        keys.sort(key = lambda x : (x[0], x[1]))
        return keys
        
    @property
    def param_values(self):
        """ A list of param values corresponding to param_keys for all mutable parameters in the circuit. 

        Returns:
            (list of float) - ordered parameter values with order corresponding
                to param_keys for all mutable parameters in the circuit.
        """
        return [self.gates[(T, key)].params[name] for T, key, name in self.param_keys]

    def set_param_values(
        self,
        values,
        ):

        """ Set the param values corresponding to param_keys for all mutable parameters in the circuit.

        Params:
            values (list of float) - ordered parameter values with order
                corresponding to param_keys for all mutable parameters in the
                circuit.
        Result:
            Parameters of self.gates are updated with new parameter values.
        """

        for k, v in zip(self.param_keys, values):
            T, key, name = k
            self.gates[(T, key)].set_param(key=name, param=v)
    
    @property
    def params(self):
        """ An OrderedDict of (T, key, param_name) : param_value for all mutable parameters in the circuit. 
            The order follows that of param_keys.

        Returns:
            (OrderedDict of (int, tuple of int, str) : float) - ordered key :
                value pairs for all mutable parameters in the circuit.
        """ 
        return collections.OrderedDict([(k, v) for k, v in zip(self.param_keys, self.param_values)])

    def set_params(
        self,
        params,
        ):

        """ Set an arbitrary number of circuit parameters values by key, value specification.
    
        Params:
            params (OrderedDict of (int, tuple of int, str) : float) - key :
                value pairs for mutable parameters to set.

        Result:
            Parameters of self.gates are updated with new parameter values.
        """
    
        for k, v in params.items():
            T, key2, name = k
            self.gates[(T, key2)].set_param(key=name, param=v)

    @property
    def param_str(self):
        """ A human-readable string describing the circuit coordinates,
            parameter names, gate names, and values of all mutable parameters in
            this circuit.
        
        Returns:
            (str) - human-readable string describing parameters in order
                specified by param_keys.
        """ 
        s = ''
        s += '%-5s %-10s %-10s %-10s: %24s\n' % ('T', 'Qubits', 'Name', 'Gate', 'Value')
        for k, v in self.params.items():
            T, key2, name = k
            gate = self.gates[(T, key2)]
            s += '%-5d %-10s %-10s %-10s: %24.16E\n' % (T, key2, name, gate.name, v)
        return s

    # > ASCII Circuit Diagrams < #

    def __str__(
        self,
        ):

        """ String representation of this Circuit (an ASCII circuit diagram). """
        return self.ascii_diagram(time_lines='both')

    def ascii_diagram(
        self,
        time_lines='both',
        ):

        """ Return a simple ASCII string diagram of the circuit.

        Params:
            time_lines (str) - specification of time lines:
                "both" - time lines on top and bottom (default)
                "top" - time lines on top 
                "bottom" - time lines on bottom
                "neither" - no time lines
        Returns:
            (str) - the ASCII string diagram
        """

        # Left side states
        Wd = int(np.ceil(np.log10(self.N)))
        lstick = '%-*s : |\n' % (2+Wd, 'T')
        for x in range(self.N): 
            lstick += '%*s\n' % (6+Wd, ' ')
            lstick += '|%*d> : -\n' % (Wd, x)

        # Build moment strings
        moments = []
        for T in range(self.nmoment):
            moments.append(self.ascii_diagram_moment(
                T=T,
                adjust_for_T=False if time_lines=='neither' else True,
                ))

        # Unite strings
        lines = lstick.split('\n')
        for moment in moments:
            for i, tok in enumerate(moment.split('\n')):
                lines[i] += tok
        # Time on top and bottom
        lines.append(lines[0])

        # Adjust for time lines
        if time_lines == 'both':
            pass
        elif time_lines == 'top':
            lines = lines[:-2]
        elif time_lines == 'bottom':
            lines = lines[2:]
        elif time_lines == 'neither':
            lines = lines[2:-2]
        else:
            raise RuntimeError('Invalid time_lines argument: %s' % time_lines)
        
        strval = '\n'.join(lines)

        return strval

    def ascii_diagram_moment(
        self,
        T,
        adjust_for_T=True,
        ):

        """ Return an ASCII string diagram for a given time moment T.

        Users should not generally call this utility routine - see
        ascii_diagram instead.

        Params:
            T (int) - time moment to diagram
            adjust_for_T (bool) - add space adjustments for the length of time
                lines.
        Returns:
            (str) - ASCII diagram for the given time moment.
        """

        circuit = self.subset([T])

        # list (total seconds) of dict of A -> gate symbol
        seconds = [{}]
        # list (total seconds) of dict of A -> interstitial symbol
        seconds2 = [{}]
        for key, gate in circuit.gates.items():
            T2, key2 = key
            # Find the first second this gate fits within (or add a new one)
            for idx, second in enumerate(seconds):
                fit = not any(A in second for A in range(min(key2), max(key2)+1))
                if fit:
                    break
            if not fit:
                seconds.append({})
                seconds2.append({})
                idx += 1
            # Put the gate into that second
            for A in range(min(key2), max(key2)+1):
                # Gate symbol
                if A in key2:
                    if gate.N == 1:
                        seconds[idx][A] = gate.ascii_symbols[0]
                    elif gate.N == 2:
                        Aind = [Aind for Aind, B in enumerate(key2) if A == B][0]
                        seconds[idx][A] = gate.ascii_symbols[Aind]
                    else:
                        raise RuntimeError('Unknown N>2 gate')
                else:
                    seconds[idx][A] = '|'
                # Gate connector
                if A != min(key2):
                    seconds2[idx][A] = '|'

        # + [1] for the - null character
        wseconds = [max([len(v) for k, v in second.items()] + [1]) for second in seconds]
        wtot = sum(wseconds)    

        # Adjust widths for T field
        Tsymb = '%d' % T
        if adjust_for_T:
            if wtot < len(Tsymb): wseconds[0] += len(Tsymb) - wtot
            wtot = sum(wseconds)    
        
        Is = ['' for A in range(self.N)]
        Qs = ['' for A in range(self.N)]
        for second, second2, wsecond in zip(seconds, seconds2, wseconds):
            for A in range(self.N):
                Isymb = second2.get(A, ' ')
                IwR = wsecond - len(Isymb)
                Is[A] += Isymb + ' ' * IwR + ' '
                Qsymb = second.get(A, '-')
                QwR = wsecond - len(Qsymb)
                Qs[A] += Qsymb + '-' * QwR + '-'

        strval = Tsymb + ' ' * (wtot + len(wseconds) - len(Tsymb) - 1) + '|\n' 
        for I, Q in zip(Is, Qs):
            strval += I + '\n'
            strval += Q + '\n'

        return strval

    def latex_diagram(
        self,
        row_params='@R=1.0em',
        col_params='@C=1.0em',
        size_params='',
        use_lstick=True,
        ):

        """ Returns a LaTeX Qcircuit diagram specification as an ASCII string. 

        Params:
            row_params (str) - Qcircuit row layout specification
            col_params (str) - Qcircuit col layout specification
            size_params (str) - Qcircuit size layout specification
            use_lstick (bool) - put lstick kets in (True) or not (False)
        Returns:    
            (str) - LaTeX Qcircuit diagram specification as an ASCII string.
        """

        strval = ''

        # Header
        strval += '\\Qcircuit %s %s %s {\n' % (
            row_params,
            col_params,
            size_params,
            )

        # Qubit lines
        lines = ['' for _ in range(self.N)]

        # Lstick  
        if use_lstick:
            for A in range(self.N):
                lines[A] += '\\lstick{|%d\\rangle}\n' % A

        # Moment contents
        for T in range(self.nmoment):
            lines2 = self.latex_diagram_moment(
                T=T,    
                one_body_printing=one_body_printing,
                variable_printing=variable_printing,
                )
            for A in range(self.N):
                lines[A] += lines2[A]
        
        # Trailing wires
        for A in range(self.N):
            lines[A] += ' & \\qw \\\\\n'

        # Concatenation
        strval += ''.join(lines)

        # Footer
        strval += '}\n'

        return strval

    def latex_diagram_moment(
        self,
        T,
        ):

        """ Return a LaTeX Qcircuit diagram for a given time moment T.

        Users should not generally call this utility routine - see
        latex_diagram instead.

        Params:
            T (int) - time moment to diagram
        Returns:
            (str) - LaTeX Qcircuit diagram for the given time moment.
        """

        circuit = self.subset([T])

        # list (total seconds) of dict of A -> gate symbol
        seconds = [{}]
        for key, gate in circuit.gates.items():
            T2, key2 = key
            # Find the first second this gate fits within (or add a new one)
            for idx, second in enumerate(seconds):
                fit = not any(A in second for A in range(min(key2), max(key2)+1))
                if fit:
                    break
            if not fit:
                seconds.append({})
                idx += 1
            # Place gate lines in circuit
            if gate.N == 1:
                A, = key2
                seconds[idx][A] = ' & \\gate{%s}\n' % gate.ascii_moments[0]
            elif gate.N == 2:
                A, B = key2
                # Special cases
                if gate.name == 'CNOT' or gate.name == 'CX':
                    seconds[idx][A] = ' & \\ctrl{%d}\n' % (B-A) 
                    seconds[idx][B] = ' & \\targ\n'
                elif gate.name == 'CZ':
                    seconds[idx][A] = ' & \\ctrl{%d}\n' % (B-A) 
                    seconds[idx][B] = ' & \\gate{Z}\n'
                elif gate.name == 'SWAP':
                    seconds[idx][A] = ' & \\qswap \\qwx[%d]\n' % (B-A) 
                    seconds[idx][B] = ' & \\qswap\n'
                # General case
                else:
                    seconds[idx][A] = ' & \\gate{%s} \\qwx[%d]\n' % (gate.ascii_moments[0], (B-A))
                    seconds[idx][B] = ' & \\gate{%s}\n' % gate.ascii_moments[1]
            else:
                raise RuntimeError('Unknown N>2 body gate: %s' % gate)

        Qs = ['' for A in range(self.N)]
        for second in seconds:
            for A in range(self.N):
                Qs[A] += second.get(A, ' & \\qw \n')

        return Qs

    # > Simulation! < #

    def simulate(
        self,
        wfn=None,
        dtype=np.complex128,
        ):

        """ Propagate wavefunction wfn through this circuit. 

        Params:
            wfn (np.ndarray of shape (2**self.N,) or None)
                - the initial wavefunction. If None, the reference state
                  \prod_{A} |0_A> will be used.
            dtype (real or complex dtype) - the dtype to perform the
                computation at. The input wfn and all gate unitary operators
                will be cast to this type and the returned wfn will be of this
                dtype. Note that using real dtypes (float64 or float32) can
                reduce storage and runtime, but the imaginary parts of the
                input wfn and all gate unitary operators will be discarded
                without checking. In these cases, the user is responsible for
                ensuring that the circuit works on O(2^N) rather than U(2^N)
                and that the output is valid.
        Returns:
            (np.ndarray of shape (2**self.N,) and dtype=dtype) - the
                propagated wavefunction. Note that the input wfn is not
                changed by this operation.
        """

        for T, wfn in self.simulate_steps(wfn, dtype=dtype):
            pass

        return wfn

    def simulate_steps(
        self,
        wfn=None,
        dtype=np.complex128,
        ):

        """ Generator to propagate wavefunction wfn through the circuit one
            moment at a time.

        This is often used as:
        
        for T, wfn1 in simulate_steps(wfn=wfn0):
            print wfn1

        Note that to prevent repeated allocations of (2**N) arrays, this
        operation allocates two (2**N) working copies, and swaps between them
        as gates are applied. References to one of these arrays are returned at
        each moment. Therefore, if you want to save a history of the
        wavefunction, you will need to copy the wavefunction returned at each
        moment by this generator. Note that the input wfn is not changed by
        this operation.

        Params:
            wfn (np.ndarray of shape (2**self.N,) or None)
                - the initial wavefunction. If None, the reference state
                  \prod_{A} |0_A> will be used.
            dtype (real or complex dtype) - the dtype to perform the
                computation at. The input wfn and all gate unitary operators
                will be cast to this type and the returned wfn will be of this
                dtype. Note that using real dtypes (float64 or float32) can
                reduce storage and runtime, but the imaginary parts of the
                input wfn and all gate unitary operators will be discarded
                without checking. In these cases, the user is responsible for
                ensuring that the circuit works on O(2^N) rather than U(2^N)
                and that the output is valid.
        Returns (at each yield):
            (int, np.ndarray of shape (2**self.N,) and dtype=dtype) - the
                time moment and current state of the wavefunction at each step
                along the propagation. Note that the input wfn is not
                changed by this operation.
        """

        # Reference state \prod_A |0_A>
        if wfn is None:
            wfn = np.zeros((2**self.N,), dtype=dtype)
            wfn[0] = 1.0
        else:
            wfn = np.array(wfn, dtype=dtype)

        # Don't modify user data, but don't copy all the time
        wfn1 = np.copy(wfn)
        wfn2 = np.zeros_like(wfn1)

        for T in range(self.nmoment):
            circuit = self.subset([T])
            for key, gate in circuit.gates.items():
                T2, key2 = key
                if gate.N == 1:
                    wfn2 = Circuit.apply_gate_1(
                        wfn1=wfn1,
                        wfn2=wfn2,
                        U=np.array(gate.U, dtype=dtype),
                        A=key2[0],
                        )
                elif gate.N == 2:
                    wfn2 = Circuit.apply_gate_2(
                        wfn1=wfn1,
                        wfn2=wfn2,
                        U=np.array(gate.U, dtype=dtype),
                        A=key2[0],
                        B=key2[1],
                        )
                else:
                    raise RuntimeError('Cannot apply gates with N > 2: %s' % gate)
                wfn1, wfn2 = wfn2, wfn1
            yield T, wfn1

    @staticmethod
    def apply_gate_1(
        wfn1,
        wfn2,
        U,
        A,
        ):

        """ Apply a 1-body gate unitary U to wfn1 at qubit A, yielding wfn2.

        The formal operation performed is,

            wfn1_LiR = \sum_{j} U_ij wfn2_LjR

        Here L are the indices of all of the qubits to the left of A (<A), and
        R are the indices of all of the qubits to the right of A (>A).

        This function requires the user to supply both the initial state in
        wfn1 and an array wfn2 to place the result into. This allows this
        function to apply the gate without any new allocations or scratch arrays.

        Params:
            wfn1 (np.ndarray of shape (2**self.N,) and a complex dtype)
                - the initial wavefunction. Unaffected by the operation
            wfn2 (np.ndarray of shape (2**self.N,) and a complex dtype)
                - an array to write the new wavefunction into. Overwritten by
                the operation.
            U (np.ndarray of shape (2,2) and a complex dtype) - the matrix
                representation of the 1-body gate.
            A (int) - the qubit index to apply the gate at.
        Result:
            the data of wfn2 is overwritten with the result of the operation.
        Returns:
            reference to wfn2, for chaining
        """

        N = (wfn1.shape[0]&-wfn1.shape[0]).bit_length()-1
        if A >= N: raise RuntimeError('A >= N')
        if U.shape != (2,2): raise RuntimeError('1-body gate must be (2,2)')
        if wfn1.shape != (2**N,): raise RuntimeError('wfn1 should be (%d,) shape, is %r shape' % (2**N, wfn1.shape))
        if wfn2.shape != (2**N,): raise RuntimeError('wfn2 should be (%d,) shape, is %r shape' % (2**N, wfn2.shape))

        L = 2**(A)     # Left hangover
        R = 2**(N-A-1) # Right hangover
        wfn1v = wfn1.view() 
        wfn2v = wfn2.view()
        wfn1v.shape = (L,2,R)
        wfn2v.shape = (L,2,R)
        np.einsum('LjR,ij->LiR', wfn1v, U, out=wfn2v)

        return wfn2

    @staticmethod
    def apply_gate_2(
        wfn1,
        wfn2,
        U,
        A,
        B,
        ):

        """ Apply a 2-body gate unitary U to wfn1 at qubits A and B, yielding wfn2.

        The formal operation performed is (for the case that A < B),

            wfn1_LiMjR = \sum_{lk} U_ijkl wfn2_LiMjR

        Here L are the indices of all of the qubits to the left of A (<A), M M
        are the indices of all of the qubits to the right of A (>A) and left of
        B (<B), and R are the indices of all of the qubits to the right of B
        (>B). If A > B, permutations of A and B and the gate matrix U are
        performed to ensure that the gate is applied correctly.

        This function requires the user to supply both the initial state in
        wfn1 and an array wfn2 to place the result into. This allows this
        function to apply the gate without any new allocations or scratch arrays.

        Params:
            wfn1 (np.ndarray of shape (2**self.N,) and a complex dtype)
                - the initial wavefunction. Unaffected by the operation
            wfn2 (np.ndarray of shape (2**self.N,) and a complex dtype)
                - an array to write the new wavefunction into. Overwritten by
                the operation.
            U (np.ndarray of shape (4,4) and a complex dtype) - the matrix
                representation of the 1-body gate. This should be packed to
                operate on the product state |A> otimes |B>, as usual.
            A (int) - the first qubit index to apply the gate at.
            B (int) - the second qubit index to apply the gate at.
        Result:
            the data of wfn2 is overwritten with the result of the operation.
        Returns:
            reference to wfn2, for chaining
        """

        N = (wfn1.shape[0]&-wfn1.shape[0]).bit_length()-1
        if A >= N: raise RuntimeError('A >= N')
        if B >= N: raise RuntimeError('B >= N')
        if A == B: raise RuntimeError('A == B')
        if U.shape != (4,4): raise RuntimeError('2-body gate must be (4,4)')
        if wfn1.shape != (2**N,): raise RuntimeError('wfn1 should be (%d,) shape, is %r shape' % (2**N, wfn1.shape))
        if wfn2.shape != (2**N,): raise RuntimeError('wfn2 should be (%d,) shape, is %r shape' % (2**N, wfn2.shape))

        U2 = np.reshape(U, (2,2,2,2))
        if A > B:
            A2, B2 = B, A
            U2 = np.einsum('ijkl->jilk', U2)
        else:
            A2, B2 = A, B

        L = 2**(A2)      # Left hangover
        M = 2**(B2-A2-1) # Middle hangover
        R = 2**(N-B2-1)  # Right hangover
        wfn1v = wfn1.view() 
        wfn2v = wfn2.view()
        wfn1v.shape = (L,2,M,2,R)
        wfn2v.shape = (L,2,M,2,R)
        np.einsum('LkMlR,ijkl->LiMjR', wfn1v, U2, out=wfn2v)

        return wfn2

    @staticmethod
    def compute_1pdm(
        wfn1,
        wfn2,
        A,
        ):

        """ Compute the 1pdm (one-particle density matrix) at qubit A. 

        The 1pdm is formally defined as,

            D_ij = \sum_{L,R} wfn1_LiR^* wfn2_LjR
        
        Here L are the indices of all of the qubits to the left of A (<A), and
        R are the indices of all of the qubits to the right of A (>A).

        If wfn1 is equivalent to wfn2, a Hermitian density matrix will be
        returned. If wfn1 is not equivalent to wfn2, a non-Hermitian transition
        density matrix will be returned (the latter cannot be directly observed
        in a quantum computer, but is a very useful conceptual quantity).

        Params:
            wfn1 (np.ndarray of shape (self.N**2,) and a complex dtype) - the bra wavefunction.
            wfn2 (np.ndarray of shape (self.N**2,) and a complex dtype) - the ket wavefunction.
            A (int) - the index of the qubit to evaluate the 1pdm at
        Returns:
            (np.ndarray of shape (2,2) and complex dtype) - the 1pdm
        """

        N = (wfn1.shape[0]&-wfn1.shape[0]).bit_length()-1
        if A >= N: raise RuntimeError('A >= N')
        if wfn1.shape != (2**N,): raise RuntimeError('wfn1 should be (%d,) shape, is %r shape' % (2**N, wfn1.shape))
        if wfn2.shape != (2**N,): raise RuntimeError('wfn2 should be (%d,) shape, is %r shape' % (2**N, wfn2.shape))

        L = 2**(A)     # Left hangover
        R = 2**(N-A-1) # Right hangover
        wfn1v = wfn1.view() 
        wfn2v = wfn2.view()
        wfn1v.shape = (L,2,R)
        wfn2v.shape = (L,2,R)
        D = np.einsum('LiR,LjR->ij', wfn1v.conj(), wfn2v)
        return D

    @staticmethod
    def compute_2pdm(
        wfn1,
        wfn2,
        A,
        B,
        ):

        """ Compute the 2pdm (two-particle density matrix) at qubits A and B. 

        The formal operation performed is (for the case that A < B),

            D_ijkl = \sum_{LMR} wfn1_LiMjR^* wfn2_LkMlR

        Here L are the indices of all of the qubits to the left of A (<A), M M
        are the indices of all of the qubits to the right of A (>A) and left of
        B (<B), and R are the indices of all of the qubits to the right of B
        (>B). If A > B, permutations of A and B and the resultant 2pdm are
        performed to ensure that the 2pdm is computed correctly.

        If wfn1 is equivalent to wfn2, a Hermitian density matrix will be
        returned. If wfn1 is not equivalent to wfn2, a non-Hermitian transition
        density matrix will be returned (the latter cannot be directly observed
        in a quantum computer, but is a very useful conceptual quantity).

        Params:
            wfn1 (np.ndarray of shape (self.N**2,) and a complex dtype) - the bra wavefunction.
            wfn2 (np.ndarray of shape (self.N**2,) and a complex dtype) - the ket wavefunction.
            A (int) - the index of the first qubit to evaluate the 2pdm at
            B (int) - the index of the second qubit to evaluate the 2pdm at
        Returns:
            (np.ndarray of shape (4,4) and complex dtype) - the 2pdm in the 
                |A> otimes |B> basis.
        """

        N = (wfn1.shape[0]&-wfn1.shape[0]).bit_length()-1
        if A >= N: raise RuntimeError('A >= N')
        if B >= N: raise RuntimeError('B >= N')
        if A == B: raise RuntimeError('A == B')
        if wfn1.shape != (2**N,): raise RuntimeError('wfn1 should be (%d,) shape, is %r shape' % (2**N, wfn1.shape))
        if wfn2.shape != (2**N,): raise RuntimeError('wfn2 should be (%d,) shape, is %r shape' % (2**N, wfn2.shape))

        if A > B:
            A2, B2 = B, A
        else:
            A2, B2 = A, B

        L = 2**(A2)      # Left hangover
        M = 2**(B2-A2-1) # Middle hangover
        R = 2**(N-B2-1)  # Right hangover
        wfn1v = wfn1.view() 
        wfn2v = wfn2.view()
        wfn1v.shape = (L,2,M,2,R)
        wfn2v.shape = (L,2,M,2,R)
        D = np.einsum('LiMjR,LkMlR->ijkl', wfn1v.conj(), wfn2v)
    
        if A > B:
            D = np.einsum('ijkl->jilk', D)

        return np.reshape(D, (4,4))

    @staticmethod
    def compute_pauli_1(
        wfn,
        A,
        ):

        """ Compute the expectation values of the 1-body Pauli operators at qubit A.

        E.g., the expectation value of the Z operator at qubit A is,

            <Z_A> = <wfn|\hat Z_A|wfn>

        These can be efficiently computed from the 1pdm (they are just an
            alternate representation of the 1pdm).

        Params:
            wfn (np.ndarray of shape (self.N**2,) and a complex dtype) - the wavefunction.
            A (int) - the index of the qubit to evaluate the Pauli measurements at.
        Returns:
            (np.ndarray of shape (4,) and real dtype corresponding to precision
                of wfn dtype) - the Pauli expectation values packed as [I,X,Y,Z].
        """

        D = Circuit.compute_1pdm(
            wfn1=wfn,
            wfn2=wfn,
            A=A,
            )

        I = (D[0,0] + D[1,1]).real
        Z = (D[0,0] - D[1,1]).real
        X = (D[1,0] + D[0,1]).real
        Y = (D[1,0] - D[0,1]).imag
        return np.array([I,X,Y,Z])

    @staticmethod
    def compute_pauli_2(
        wfn,
        A,
        B,
        ):

        """ Compute the expectation values of the 2-qubit Pauli operators at
            qubits A and B.

        E.g., the expectation value of the Z operator at qubit A and the X
        operator at qubit B is,

            <Z_A X_B> = <wfn|\hat Z_A \hat X_B|wfn>

        These can be efficiently computed from the 2pdm (they are just an
            alternate representation of the 2pdm).

        Params:
            wfn (np.ndarray of shape (self.N**2,) and a complex dtype) - the wavefunction.
            A (int) - the index of the first qubit to evaluate the Pauli measurements at.
            B (int) - the index of the second qubit to evaluate the Pauli measurements at.
        Returns:
            (np.ndarray of shape (4,4) and real dtype corresponding to precision
                of wfn dtype) - the Pauli expectation values packed as [I,X,Y,Z].
        """

        D = Circuit.compute_2pdm(
            wfn1=wfn,
            wfn2=wfn,
            A=A,
            B=B,
            )

        Pmats = [Matrix.I, Matrix.X, Matrix.Y, Matrix.Z]
        G = np.zeros((4,4))
        for A, PA in enumerate(Pmats):
            for B, PB in enumerate(Pmats):
                G[A,B] = np.sum(np.kron(PA, PB).conj() * D).real

        return G

