import timeit

test_statement = '''
t.name_or_id = 1
'''

def main():

    print(timeit.timeit(test_statement, setup='from instruct import Test;t = Test()'))
    print(timeit.timeit(test_statement, setup='from instruct import TestOptimized as Test;t = Test()'))

    print("This function is easily called using 'python -m module_template'!")

if __name__ == '__main__':
    main()
