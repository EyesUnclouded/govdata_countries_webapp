from multiprocessing import Pool

def worker(x):
    return x*x

if __name__ ==  '__main__':
    num_processors = 3
    p=Pool(processes = num_processors)
    output = p.map(worker,[i for i in range(0,3)])
    print(output)