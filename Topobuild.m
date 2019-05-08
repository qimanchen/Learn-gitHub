function [ starxdegree ] = Topobuild( numnode,degree )
# numnode -- rack的数量
starxdegree=inf*ones(numnode);
# 生成初始的
# ones 产生全1的矩阵
# find 寻找矩阵中满足指定条件的元素
for i=1:numnode
    temp=1:numnode;
    for k=i+1:numnode
        if length(find(starxdegree(k,:)==1))>=degree
            temp(find(temp==k))=[];
        end
    end
    temp(1:i)=[];
    findnode=degree-length(find(starxdegree(i,:)==1));
    temp=temp(randperm(length(temp)));
    if length(temp)>=findnode
        temp=temp(1:findnode);
        for j=1:findnode
            starxdegree(i,temp(j))=1;
            starxdegree(temp(j),i)=1;
        end
    end
end
end
