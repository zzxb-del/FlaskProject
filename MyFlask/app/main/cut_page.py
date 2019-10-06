class Pager:
    """
        flask分页通过sqlalachemy查询进行分页
        offset 偏移，开始查询的位置
        limit 单页条数
        分页器需要具备的功能
        页码
        分页数据
        是否第一页
        是否最后一页
    """
    def __init__(self,data,page_size):
        """
                data: 要分页的数据
                page_size: 每页多少条
        """
        self.data = data  #总数据
        self.page_size =page_size  #单页数据
        self.is_start = False
        self.is_end = False
        self.page_count = len(data)
        self.next_page = 0  #下一页
        self.previous_page = 0 #上一页
        self.page_number = self.page_count/page_size
        #(data+page_size-1)//page_size
        if self.page_number == int(self.page_number):
            self.page_number = int(self.page_number)
        else:
            self.page_number = int(self.page_number)+1

        self.page_range = range(1,self.page_number+1)   #页码范围

    def page_data(self,page):
        """
                返回分页数据
                :param page: 页码
                page_size = 10
                1    offect 0  limit(10)
                2    offect 10 limit(10)
                page_size = 10
                1     start 0   end  10
                2     start 10   end  20
                3     start 20   end  30
        """
        self.next_page = int(page)+1
        self.previous_page = int(page)-1
        if page <= self.page_range[-1]:
            page_start = (page - 1)*self.page_size
            page_end = page*self.page_size
            data = self.data[page_start:page_end]
            if page == 1 :
                self.is_start = True
            else:
                self.is_start = False
            if page == self.page_range[-1]:
                self.is_end = True
            else:
                self.is_end = False
        else:
            data = ["没有数据"]
        return data