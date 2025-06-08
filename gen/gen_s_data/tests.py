import structured_data_gen as stdg

if __name__ == '__main__':
    for i in range(10):
        print(stdg.prob_info_or_None(lambda _: 4, 0.1))
    