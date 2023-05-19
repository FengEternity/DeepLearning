> 错误代码：RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x80736 and 60000x2)

* 在开始训练时网络结构总是对应不上，通过打印每一次forward() 函数中每一步骤的 s.shape() 发现，在运行到第16个 batch_size 时出现错误
* 可以推测出，至少前面的 15 个 batch_size 是正确的
* 猜测：是否是因为一个 epoch 中的最后一个 batch_size 张数不对，所以在定义 DataLoader 时加上 drop_last = true，即舍弃最后一个不整的 batch_size，结果发现不是这一问题
* 最后检查数据时发现，在定义 test_transform 时，将图片归一化为 252，这也解释了为什么在第 16 个 batch_szie 时才发生错误 