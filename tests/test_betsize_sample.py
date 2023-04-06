from utils import classify_betsize


def test_betsize_exact():
    ans = classify_betsize(1)
    print(ans)
    assert ans == 3, ans


def test_betsize_exact2():
    ans = classify_betsize(0.5)
    print(ans)
    assert ans == 7, ans


def test_betsize_exact2():
    ans = classify_betsize(0.05)
    print(ans)
    assert ans == 10, ans


# def test_betsize_sample():
#     out = []
#     for _ in range(100):
#         out.append(classify_betsize(0.26))
#     c = Counter(out)
#     print(c)
#     print([action_to_str[k] for k in c.keys()])
#     asdf
