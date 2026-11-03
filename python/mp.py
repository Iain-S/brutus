from multiprocessing import Pool
from myf import f

def main():
    with Pool(5) as p:
        results = p.map(f, [1,2,3])
    print(results)

if __name__ == "__main__":
    main() 