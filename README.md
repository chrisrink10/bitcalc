# bitcalc

Bitwise operations in C and other derivative languages can be a bit 
challenging to visualize and understand if you don't use them very often.

Now, you can use this simple expression calculator to see a visual 
representation of the bitwise operations to verify your intuition or to
learn.

Bitcalc supports all standard C bitwise operators (`<<`, `>>`, `&`, `|`,
`^`, and `~`) and the basic C arithmetic operators (`+`, `-`, `*`, `/`, and
`%`). All of the supported operators follow standard C precedence and 
associativity rules. Operator precedence can be changed using parentheses,
as is typically permitted in C. 

## Getting Started

Bitcalc can be installed easily using pip:

    pip install https://github.com/chrisrink10/bitcalc
    
You can start bitcalc from your console using the `bitcalc` command. 

## Examples

Simple operations show the bitwise operation in the format typically used
by students learning basic arithmetic operations to help clarify what is
happening at a bit level.

    >>> (1 | 10)
    
    (1 | 10)
        00000001
     |  00001010
    ------------
        00001011
    11

More complex expressions are solved one-by-one in order of precedence for
each sub-expression to help make clear how each operand in the final 
expression was calculated.

    >>> (81 & (1 << 3))
    
    (1 << 3)
        00000001
     <<        3
    ------------
        00001000
    
    (81 & (1 << 3))
        01010001
     &  00001000
    ------------
        00000000
    0

Bitcalc supports arbitrary complex expressions.

    >>> (81 & (1 << 3)) | (45 ^ (3 << 2))
    
    (1 << 3)
        00000001
     <<        3
    ------------
        00001000
    
    (81 & (1 << 3))
        01010001
     &  00001000
    ------------
        00000000
    
    (3 << 2)
        00000011
     <<        2
    ------------
        00001100
    
    (45 ^ (3 << 2))
        00101101
     ^  00001100
    ------------
        00100001
    
    ((81 & (1 << 3)) | (45 ^ (3 << 2)))
        00000000
     |  00100001
    ------------
        00100001
    33

## License

MIT License