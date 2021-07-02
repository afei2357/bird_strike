
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
from numpy import nan 
import random


# In[2]:

order_df = pd.read_csv('order.table.xls',header=0,sep='\t')
dna_df = pd.read_csv('DNA.table.xls',header=0,sep='\t')
delivery_df = pd.read_csv('delivery.table.xls',header=0,sep='\t')
 


# In[3]:

# order_df
# dna_df
# delivery_df


# In[4]:

order_df['receive_date'] = delivery_df['receive_date']


# In[5]:

# order_df['receive_date'] 


# In[6]:

order_df['receive_date'] = order_df['receive_date'].str.strip(' 00:00:00').str.replace('-','.')


# In[7]:

# 部分样品编码含有反斜杠，这些反斜杠在数据保存的路径被‘-’代替了 
order_df['sample_code_format'] =  order_df['sample_code'].str.replace('/','-').str.replace(' ','-').str.replace(u'加急','jiaji')


# In[8]:

order_df.iloc[1958,:]


# In[9]:

# 找到那些不含有日期的字符，使他为nan：
order_df[order_df['receive_date'] == '.'] = nan
# 填充空缺的日期：
order_df['receive_date'].fillna(method='ffill',axis=0,inplace=True)



# In[10]:

# order_df[order_df['receive_date'].str.contains('\b\.\b')]

# 由于日期格式不统一，所以 将字符串都转为日期类型：
order_df['receive_date'] = order_df['receive_date'].apply(pd.to_datetime,infer_datetime_format=True)


# In[11]:

# order_df['receive_date'].apply(pd.to_datetime,infer_datetime_format=True)
# 再将日期转回字符串：
order_df['receive_date'] = order_df['receive_date'].apply(lambda x : x.strftime('%Y%m%d'))


# In[12]:

length_df = len(order_df['receive_date'])
order_df['random_num'] = [str(random.randint(10000, 99999)) for i in range(length_df) ]


# In[13]:

# order_df.random_num
order_df['order_num'] = order_df['receive_date']+ order_df['random_num'] 

# order_df['order_num'] 


# In[14]:

# 由于有部分测序路径的文件名是以航班号而非样本名来命名，所以有必要吧航班号放进来：
order_df['event_flight']  = delivery_df['event_flight']


# In[15]:

# 测试填空值：
# df = pd.DataFrame(np.random.randn(6,3))
# df.iloc[1:4,1] = nan
# df.iloc[2:5,2] = nan
# df.fillna(method='ffill',axis=0)


# In[16]:

order_df['id'] = order_df.index +1 
# del order_df['random_num']
# del order_df['receive_date']
order_df.to_csv('order_df.tsv',encoding='utf_8_sig',index=False)
print('---1')


# In[17]:

#有些样品是没有样品名的，先挑出来，以后在处理这些样品。
order_df_null_samplecode = order_df[order_df['sample_code'].isnull()]
order_df_null_samplecode.to_csv('order_df_null_samplecode.tsv',encoding='utf_8_sig',index=False)


# In[18]:


# order_df.loc[[8,9,10],'sample_code']



# In[19]:

dna_df.to_csv('dna_df.tsv',encoding='utf_8_sig',index=False)


# In[20]:

delivery_df.to_csv('delivery_df.tsv',encoding='utf_8_sig',index=False)


# In[ ]:




# In[21]:

path_df = pd.read_csv('airport.csv',header=0,sep=',')


# In[22]:

path_df.head


# In[23]:

result_df = pd.merge(order_df,path_df,left_on=['sample_code_format'],right_on=['sample_code'],how='outer')
result_df_event_flight = pd.merge(order_df,path_df,left_on=['event_flight'],right_on=['sample_code'],how='inner') # 


# In[24]:

result_df.to_csv('result_df.tsv',encoding='utf_8_sig',index=False)
result_df_event_flight.to_csv('result_df_event_flight.tsv',encoding='utf_8_sig',index=False)


# In[25]:

result_df


# In[26]:

s = 'ZBAD2021-加急1'
s.replace('加急','jiaji')


# In[27]:

# s


# In[28]:

# order_df.iloc[[1849,1850],:]


# In[29]:

print('--')


# In[30]:

result_df.path


# In[31]:

from app import create_app
app = create_app()
app_context =  app.app_context()
app_context.push()



from app.models1 import *
from app.models import *
import random
from datetime import datetime


# In[32]:


result_df['id'] = result_df['id'].apply(lambda x : int(x) if not pd.isnull(x) else 0)
# 导入数据库


# In[33]:

# result_df['create_time'] = pd.to_datetime(result_df['create_time'],infer_datetime_format=True )
# result_df['sample_date'] = pd.to_datetime(result_df['sample_date'],infer_datetime_format=True )
# result_df['receive_date'] = pd.to_datetime(result_df['receive_date'],infer_datetime_format=True )
# result_df['report_date'] = pd.to_datetime(result_df['report_date'],infer_datetime_format=True )
# print(type(result_df['order_date']))
# result_df['id'] = result_df['id'].apply(lambda x :  int(x)  if x else None  )
# result_df['id'] = result_df['id'].astype('int64')
# print(result_df.id )

print(result_df['id'])


# In[ ]:




# In[34]:

old_id = None
i = 0
for ix,val in result_df.iterrows():
    data = val.to_dict()
    id =  data.get('id')
    if not id :
        continue   
    else:
#         print(val.get('id'))        
        
        o = OrderSeq()
        o.from_dict(data)
#         print(o.id)
#         print(data.get('id'))
        db.session.add(o)
        
    if val.get('path') and not pd.isnull(val.get('path')):
        seqData = SeqData()
        seqData.from_dict(data)
 
        with open (val.get('path')) as fh:
            raw_data = fh.read()
            seqData.raw_data = raw_data 
            
        o.seqData.append(seqData)
        db.session.add(seqData)
    
#     old_id = data.get('id')
    
    i+= 1
    if i%100 == 0:
        db.session.commit()
        
db.session.commit()
print('finish ')
app_context.pop()        
        



# In[ ]:

# OrderSeq.__table__.columns.keys()


# In[ ]:

l = [1,2,3]
l


# In[ ]:

db.session.rollback()


# In[ ]:


