function [ starxdegree ] = Topobuild( numnode,degree )
# numnode -- rack的数量
starxdegree=inf*ones(numnode);
# 生成初始的
# ones 产生全1的矩阵
# find 寻找矩阵中满足指定条件的元素
for i=1:numnode
    temp=1:numnode;
    for k=i+1:numnode
		# length(find(starxdegree(k,:)==1)) -- 寻找矩阵中第k行中等于1的元素的个数，满足degree个数的节点
        if length(find(starxdegree(k,:)==1))>=degree
			# find函数返回的是寻找找的元素的index索引位置
			# 清除temp中等于k的元素，pop出去
            temp(find(temp==k))=[];
        end
    end
    temp(1:i)=[];# 去除temp中第一个到第i个元素
	# 寻找到第i行（第i个节点）中等于1的节点
    findnode=degree-length(find(starxdegree(i,:)==1));
	# 重新排序temp
	# python中可以使用random.shuffle(list)实现randperm的功能
	# 可以通过random.sample(list,n) -- 从list中选取n个随机的元素
    temp=temp(randperm(length(temp)));
	# 寻找到相应直连节点
    if length(temp)>=findnode
        temp=temp(1:findnode);
        for j=1:findnode
            starxdegree(i,temp(j))=1;
            starxdegree(temp(j),i)=1;
        end
    end
end
end
