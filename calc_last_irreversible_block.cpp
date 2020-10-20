#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

#define GRAPHENE_100_PERCENT 100
#define GRAPHENE_IRREVERSIBLE_THRESHOLD 70

template<typename T>
void print(const vector<T>& v){
    for(size_t i=0; i<v.size(); i++) {
        cout << v[i] << " ";
    }
    cout << endl;
}

//g++ test.cpp -std=c++11
void test()
{
    int arr[] = {206193, 206191, 206194, 206187, 206186, 206185, 206188, 206189, 206192, 206190, 197213};
    int last_irreversible_block_num = 206187;
    size_t size = sizeof(arr)/sizeof(int); 
    vector<int> vec(arr, arr+size);
    print(vec);
    size_t offset = ((GRAPHENE_100_PERCENT - GRAPHENE_IRREVERSIBLE_THRESHOLD) * vec.size() / GRAPHENE_100_PERCENT); // 不可逆区块偏移量计算
    cout << "offset: " << offset << endl;
    std::nth_element(vec.begin(), vec.begin() + offset, vec.end(), [](int a, int b) { return a < b; });
    print(vec);
    //uint32_t new_last_irreversible_block_num = wit_objs[offset]->last_confirmed_block_num;
    int new_last_irreversible_block_num = vec[offset];
    cout << "new: " << new_last_irreversible_block_num << endl;
    cout << "old: " << last_irreversible_block_num << endl;

    cout << "\n\nsort :" << endl;
    std::sort(vec.begin(), vec.end());
    print(vec);
}

void test2()
{
    //int arr[] = {193, 191, 194, 187, 186, 185, 188, 189, 192, 190, 163};
    //int arr[] = {207004, 207003, 207009, 207011, 207000, 207010, 207001, 207002, 207008, 207007, 197213};
    //int arr[] = {93, 91, 94, 87, 86, 85, 88, 89, 92, 90, 63};
    int arr[] = {93, 91, 94, 87, 86, 85, 88, 89, 92, 45, 63};
    size_t size = sizeof(arr)/sizeof(int);
    vector<int> vec(arr, arr+size);
    print(vec);
    size_t offset = ((GRAPHENE_100_PERCENT - GRAPHENE_IRREVERSIBLE_THRESHOLD) * vec.size() / GRAPHENE_100_PERCENT); // 不可逆区块偏移量计算
    cout << "offset: " << offset << ", value: " << vec[offset] << endl;
    std::nth_element(vec.begin(), vec.begin() + offset, vec.end(), [](int a, int b) { return a < b; });
    print(vec);
    int new_num = vec[offset];
    cout << "new_num: " << new_num << endl;

    cout << "\n\nsort :" << endl;
    std::sort(vec.begin(), vec.end());
    print(vec);
}

int main()
{
	//test();
    test2();
    return 0;
}
