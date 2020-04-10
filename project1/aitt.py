from django.shortcuts import render
from django.http import HttpResponse
import mysql.connector

def run(rq):

    
    # coding: utf-8

    # In[1]:


    #importing the libraries
    import pandas as pd
    import numpy as np
    import mysql.connector


    # In[ ]:


    mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="aitt"
        )

    mycursor = mydb.cursor()


    # In[ ]:


    #converting the tables to data frames
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM Division_input")

    myresult = mycursor.fetchall()

    Division = []
    Subject = []
    Hours_in_week = []
    Combined = []
    batches = []

    for i in range(len(myresult)):
        Division.append(myresult[i][0])
        Subject.append(myresult[i][1])
        Hours_in_week.append(myresult[i][2])
        Combined.append(myresult[i][3])
        batches.append(myresult[i][4])
        
    division = pd.DataFrame({'Division':Division,'Subject':Subject,'hours in week':Hours_in_week, 'Combined':Combined, 'batches':batches})

    for i in range(len(division)):
        if(division['Combined'][i] == 'nan'):
            division['Combined'][i] = np.nan 
        division['hours in week'][i] = int(division['hours in week'][i])
        division['batches'][i] = int(division['batches'][i])
            
    #converting the tables to data frames

    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM Teachers_input")

    myresult = mycursor.fetchall()

    teacher = []
    Subject = []
    div = []


    for i in range(len(myresult)):
        teacher.append(myresult[i][0])
        Subject.append(myresult[i][1])
        div.append(myresult[i][2])

    teacher = pd.DataFrame({'Teacher':teacher,'Subject':Subject,'Divisions':div})

    #converting the tables to data frames
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM CR_input")

    myresult = mycursor.fetchall()

    cr = []
    Subject = []
    div = []


    for i in range(len(myresult)):
        cr.append(myresult[i][0])
        Subject.append(myresult[i][2])
        div.append(myresult[i][1])

    cr = pd.DataFrame({'cr':cr,'division':div,'Subject':Subject})

    for i in range(len(cr)):
        if(cr['division'][i] == 'nan'):
            cr['division'][i] = np.nan  
        if(cr['Subject'][i] == 'nan'):
            cr['Subject'][i] = np.nan      


    # In[ ]:


    #importing the division file
    #division = pd.read_excel('division_tt.xlsx', encoding='utf-8')
    #division.head()

    # importing the class room file
    #cr = pd.read_excel('cr_tt.xlsx', encoding='utf-8')
    cr['empty'] = 0
    for i in range(len(cr)):
        if(cr['division'].isnull()[i] and cr['Subject'].isnull()[i]):
            cr['empty'][i] = 1

    #cr.head()

    #importing the teacher file
    #teacher = pd.read_excel('teacher_tt.xlsx', encoding='utf-8')
    #teacher.head()

    #creating the base of data frame
    empty_list = [0,'null']
    rows = ['8:00 AM-9:00 AM','9:00 AM-10:00 AM','10:00 AM-11:00 AM','11:00 AM-12:00 PM','12:00 PM-1:00 PM','1:00 PM-2:00 PM','2:00 PM-3:00 PM','3:00 PM-4:00 PM','4:00 PM-5:00 PM','5:00 PM-6:00 PM']
    column = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']


    # getting the list of divisions
    division_list = division['Division'].copy()
    for i in range(len(division_list)):
        division_list[i].split('-')
        division_list[i] = division_list[i][0]
        

    division_list = division_list.unique()


    # getting the list of teachers
    teacher_list = teacher['Teacher'].copy()
    teacher_list = teacher_list.unique()



    # getting the list of class rooms available
    cr_list = cr['cr'].copy()
    cr_list = cr_list.unique()




    # creating a dummy timetable for each division
    division_df = []
    for i in range(len(division_list)):
        new_str = division_list[i]
        
        new_str = pd.DataFrame( index = rows, columns = column)
        new_str.iloc[0,0] = empty_list
        new_str = new_str.ffill(axis = 0)
        new_str = new_str.ffill(axis = 1)
        division_df.append(new_str)

        
    # creating a dummy timetable for each teacher
    teachers_df = []
    for i in range(len(teacher_list)):
        new_str = teacher_list[i]
        
        new_str = pd.DataFrame( index = rows, columns = column)
        new_str.iloc[0,0] = empty_list
        new_str = new_str.ffill(axis = 0)
        new_str = new_str.ffill(axis = 1)
        teachers_df.append(new_str)   

        
    # creating a dummy timetable for each class room
    cr_df = []
    for i in range(len(cr_list)):
        new_str = cr_list[i]
        
        new_str = pd.DataFrame( index = rows, columns = column)
        new_str.iloc[0,0] = empty_list
        new_str = new_str.ffill(axis = 0)
        new_str = new_str.ffill(axis = 1)
        cr_df.append(new_str)


    # In[ ]:


    def lunch_break(start,end,current):
        
        current = current.split('-')
        current = current[0].split(' ')
        am_pm = current[1]
        current = current[0].split(':')
        current = int(current[0])
        if(am_pm == 'PM'):
            if(current%12 != 0):
                current = current + 12

        start = '11:00 AM'        
        start = start.split(' ')
        am_pm = start[1]
        start = start[0].split(':')
        start = int(start[0])
        if(am_pm == 'PM'):
            if(start%12 != 0):
                start = start + 12

        end = '2:00 PM'        
        end = end.split(' ')
        am_pm = end[1]
        end = end[0].split(':')
        end = int(end[0])
        if(am_pm == 'PM'):
            if(end%12 != 0):
                end = end + 12

        lunch = 0
        
        for i in range(start,end):
            if(current == i):
                lunch = 1
                break
        return lunch       


    # In[ ]:


    for divs in range(len(division_list)):
        
        div = division_list[divs]
        df1 = division.where(division['Division'].str.contains(div))
        df1 = df1[pd.notnull(df1['Division'])]
        df1 = df1.reset_index(drop=True)
        completed = []
        
        for i in range(len(df1)):
            completed.append(0)
        df1['completed'] = completed
        df1.head()


        df2 = teacher.where(teacher['Divisions'].str.contains(div))
        df2 = df2[pd.notnull(df2['Divisions'])]
        df2 = df2.reset_index(drop=True)
        df2


        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
        check = [0,0,0,0,0,0]
        lunch_breaks = [0,0,0,0,0,0]
        days_check = [list(a) for a in zip(days, check,lunch_breaks)]
        days_check

        for i in range(len(df1)):
            a = int(df1['batches'][i])
            df1['batches'][i] = a


        unique_list = []
        for i in range(len(df1['batches'])):
            if int(df1['batches'][i]) not in unique_list:
                unique_list.append(int(df1['batches'][i]))
        unique_list.sort()

        #groups = []
        #for i in range(len(unique_list)):
        #    groups.append(i+1)

        #group_type = []
        #for i in range(len(df1)):
        #    dummy2 = df1['batches'][i]
        #    index_of_group = unique_list.index(dummy2)
        #    dummy2 = groups[index_of_group]
        #    group_type.append(dummy2)
        #df1['group_type'] = group_type        

        # Extracting all the subjects in a particular group
        practical_subjects = df1['Subject'].where(df1['batches'] == unique_list[1]).dropna()
        practical_subjects = practical_subjects.tolist()

        #creating batches with divisions name in it

        batch_name = []
        for i in range(unique_list[1]):
            x = div + str(i+1)
            batch_name.append(x)

        #creating two dataframes for tracking whether the batches have been allocated and that only 1 lab is there per day    
        column1 = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
        column2 = practical_subjects
        rows1 = batch_name
        batches_tt = pd.DataFrame(0,index = rows1, columns = column1)
        batches_practical = pd.DataFrame(0,index = rows1, columns = column2)
        
        if(len(practical_subjects) >= len(batch_name)):
            iterations = len(batch_name)
            iterations1 = len(practical_subjects)
        else:
            iterations = len(practical_subjects)
            iterations1 = len(batch_name)


        for n in range(iterations1):
            practical = []
            batch = []

            if(len(practical_subjects) >= len(batch_name)):
                for j in range(iterations):
                    if(0 in batches_practical[practical_subjects[(n+j)%(len(practical_subjects))]].tolist()):
                        practical.append(practical_subjects[(n+j)%(len(practical_subjects))])
                        for z in range(len(batch_name)):
                            if(batches_practical[practical_subjects[(n+j)%(len(practical_subjects))]][(z+j)%(len(batch_name))] == 0):
                                batch.append((z+j)%(len(batch_name)))
                                break
                    else:
                        break
            else:
                for j in range(iterations):
                    if(0 in batches_practical[practical_subjects[(j)%(len(practical_subjects))]].tolist()):
                        practical.append(practical_subjects[(j)%(len(practical_subjects))])
                        for z in range(len(batch_name)):
                            if(batches_practical[practical_subjects[(j)%(len(practical_subjects))]][(z+j+n)%(len(batch_name))] == 0):
                                batch.append((z+j+n)%(len(batch_name)))
                                break
                    else:
                        break
            
            # getting the teachers index no. and cr index no.        
            t_practicals = []
            cr_practicals = []
            # these list is created to sort the cr according to the no. of options of classroom a practical gets 
            no_of_cr = []

            for j in range(len(practical)):
                sub = practical[j]
                cr_allocated = 0
                dummy_df = cr.where(cr['Subject'] == sub)
                dummy_df = dummy_df[pd.notnull(dummy_df['Subject'])]
                no_of_cr.append(len(dummy_df))

            dummy_list1 = []
            dummy_list2 = []

            for j in range(len(practical)):
                dummy_list = no_of_cr.copy()
                dummy_list.sort()
                index = no_of_cr.index(dummy_list[0])
                no_of_cr[index] = 1000

                dummy_list1.append(practical[index])
                dummy_list2.append(batch[index])

            practical = dummy_list1
            batch = dummy_list2

            for j in range(len(practical)):
                sub = practical[j]
                cr_allocated = 0
                dummy_df = cr.where(cr['Subject'] == sub)
                dummy_df = dummy_df[pd.notnull(dummy_df['Subject'])]

                #k = len(dummy_df)
                for z in range(len(dummy_df)):
                    cr_div = dummy_df['cr'].iloc[z]
                    if(cr_div in cr_practicals):
                        continue
                    else:    
                        cr_practicals.append(cr_div)
                        break

                teacher_sub = df2['Teacher'].where(df2['Subject'] == sub ).dropna()
                teacher_sub = teacher_sub.iloc[0]
                dummy_df = teacher.where(teacher['Teacher'] == teacher_sub)
                dummy_df = dummy_df[pd.notnull(dummy_df['Teacher'])]

                teacher_no_index = np.where(teacher_list == teacher_sub)[0]
                teacher_no_index = teacher_no_index.astype(int)
                teacher_no_index = teacher_no_index[0]
                t_practicals.append(teacher_no_index)

            cr_practicals_index = []    

            for j in range(len(practical)):
                cr_div = cr_practicals[j]
                cr_no_index = np.where(cr_list == cr_div)[0]
                cr_no_index = cr_no_index.astype(int)
                cr_no_index = cr_no_index[0]
                cr_practicals_index.append(cr_no_index)
            for j in range(6):

                    if(len(practical) == 1):
                        dummy_list = batches_tt[column1[j]].tolist()
                        if(1 in dummy_list):
                            continue

                    practical_allocated = 0
                    for z in range(len(batch)):


                        if(batches_practical.iloc[batch[z]][practical[z]] == 1):
                            practical_allocated = 1    

                    if(practical_allocated == 1):
                        
                        break


                    batch_allocated = 0
                    for z in range(len(batch)):
                        if(batches_tt.iloc[batch[z]][j] == 1):
                            batch_allocated = 1

                    

                    if(batch_allocated == 1):
                        continue    

                    for k in range(10):
                        # checking if the class room is free
                        dummy_list = []
                        for z in range(len(cr_practicals_index)):
                            dummy_list.append(cr_df[cr_practicals_index[z]][days[j]][k][0] == 0)
                        if((False in dummy_list) != True):
                            # getting the index pf particular teachers tt

                            dummy_list = []
                            for z in range(len(t_practicals)):
                                dummy_list.append(teachers_df[t_practicals[z]][days[j]][k][0] == 0)
                            #checking if the teacher is free
                            if((False in dummy_list) != True):

                                # getting the index of the tt of particular division
                                div_index = np.where(division_list == div)[0]

                                div_index = div_index.astype(int)
                                div_index = div_index[0]

                                #checking if the division is free
                                if(division_df[div_index][days[j]][k][0] == 0 and days_check[j][1] == 0):
                                    #getting the total no. of hours that subject is conducted in a week

                                    dummy_df1 = []
                                    for z in range(len(cr_practicals_index)):
                                        dummy_df1.append(cr_df[cr_practicals_index[z]].copy())
                                    dummy_df2 = []
                                    for z in range(len(cr_practicals_index)):
                                        dummy_df2.append(teachers_df[t_practicals[z]].copy())

                                    dummy_df3 = division_df[div_index].copy()
                                    flag_break = 0
                                    try:
                                        for i in range(2):
                                            for z in range(len(dummy_df1)):
                                                if(dummy_df1[z].iloc[k+i,j][0] == 1):
                                                    
                                                    flag_break = 1
                                            for z in range(len(dummy_df2)):
                                                if(dummy_df2[z].iloc[k+i,j][0] == 1):
                                                    
                                                    flag_break = 1
                                            if(dummy_df3.iloc[k+i,j][0] == 1):
                                                
                                                flag_break = 1 
                                            
                                    except:
                                        flag_break = 1
                                        

                                    if(flag_break == 1):
                                        break

                                    # allocating the lecture in all the time tables
                                    hours = 2
                                    for i in range(int(hours)):
                                        div_details = ""
                                        for z in range(len(cr_practicals_index)):
                                            cr_df[cr_practicals_index[z]].iat[k+i,j] = [3,div +" "+ cr_practicals[z] + " " + batch_name[batch[z]]]


                                            teachers_df[t_practicals[z]].iat[k+i,j] = [3,div +" "+ cr_practicals[z] +" "+ batch_name[batch[z]]]

                                            div_details = div_details+" "+practical[z]+" "+batch_name[batch[z]]+" "+cr_practicals[z] + "    "

                                        division_df[div_index].iat[k+i,j] = [3,div_details]
                                        
                                    #trying to allocate lunch to the division if the time is right
                                    lunch = 0
                                    try:
                                        current = division_df[div_index].index[k+hours]
                                        lunch = lunch_break('11:00 AM','2:00 PM',current)
                                        print(lunch)
                                        print(div)


                                    except:
                                        pass

                                    # trying to give a break to the teacher
                                    try:
                                        teachers_df[teacher_no_index].iat[k+hours,j] = [1,'break']

                                        if(days_check[j][2] == 0):
                                            if(lunch == 1):
                                                if(division_df[div_index].iloc[k+hours,j][0] == 0):

                                                    division_df[div_index].iat[k+hours,j] = [1,'lunch break']
                                    except:

                                        pass

                                    for z in range(len(batch)):
                                        batches_tt.iloc[batch[z]][j] = 1
                                        batches_practical.iloc[batch[z]][practical[z]] = 1
                                        

                                    #df1['hours in week'][df1['hours in week'].where(df1['Subject'] == sub).dropna().index[0]] = df1['hours in week'][df1['hours in week'].where(df1['Subject'] == sub).dropna().index[0]] - hours

                                    # checking whetehr the maximum limit to the no. of lectures in a day has been reached or not
                                    #div_hour = 0
                                    #for i in range(len(division_df)):
                                    #    div_hour = div_hour + division_df[div_index].iloc[:,j][i][0]
                                    #if(div_hour>=div_max_limit):
                                    #   days_check[j][1] = 1   



                                    #checkking whether the subject hours have been completed
                                    #checking whether all the subjects of the division have been completed or not
                                    #if(df1['hours in week'].where(df1['Subject'] == sub).dropna().reset_index(drop=True)[0] == 0):
                                    #   df1['completed'][df1['hours in week'].where(df1['Subject'] == sub).dropna().index[0]] = 1
                                    #   lec_allocated = 1
                                    #   div_not_completed = 0
                                    #   for i in range(len(df1)):
                                    #        if(df1['completed'][i] == 0):
                                    #            div_not_completed = 1
                                    #    if(div_not_completed == 0):
                                    #        flag_div_completed = 1

                                    #    print(flag_div_completed)
                                #     break
                                    #else:
                                    #    lec_allocated = 1
                                    #    break


                                    for z in range(len(practical_subjects)):
                                        flag_complete = 1
                                        for b in range(len(batch_name)):
                                            if(batches_practical.iloc[b][z] == 0):

                                                flag_complete = 0
                                        if(flag_complete == 1):
                                            dummy_list = df1.index[df1['Subject'] == practical_subjects[z]].tolist()
                                            dummy_list = dummy_list[0]

                                            df1['completed'][dummy_list] = 1

                                    break    

                                else:
                                    continue



                            else:
                                continue

                        else:
                            continue


        flag_div_completed = 0 # flag becomes 1 when all the subjects in that division have been allocated
        i = 0 # for subject
        div_max_limit = 8
        while(flag_div_completed == 0):
            # select the subject and find out the classes where the subject can be conducted
            sub = df1['Subject'][i]
            dummy_df = cr.where(cr['Subject'] == sub)
            dummy_df = dummy_df[pd.notnull(dummy_df['Subject'])]
            if(dummy_df.empty):
                # subject is a theory / tutorial and will be condected in a class
                dummy_df = cr.where(cr['division'] == div) 
                dummy_df = dummy_df[pd.notnull(dummy_df['division'])]
                if(dummy_df.empty):
                    dummy_df = cr.where(cr['empty'] == 1)
                    dummy_df = dummy_df[pd.notnull(dummy_df['empty'])]
                    cr_div = dummy_df['cr'].iloc[0]
                    cr = cr.append(pd.Series([cr_div,div,np.NaN,0],index=cr.columns),ignore_index = True)
                    cr_no_index = np.where(cr_list == cr_div)[0]
                    cr_no_index = cr_no_index.astype(int)
                    # the class room where the subject can be conducted
                    cr_no_index = cr_no_index[0]
                else:    
                    cr_div = dummy_df['cr'].iloc[0]
                    cr_no_index = np.where(cr_list == cr_div)[0]
                    cr_no_index = cr_no_index.astype(int)
                    # the class room where the subject can be conducted
                    cr_no_index = cr_no_index[0]

                #if subject hours are not completed then set lecture allocated to 0
                if(df1['completed'].iloc[i] == 0):
                    lec_allocated = 0
                # running the loop for 6 days a week
                for j in range(7):

                    if(lec_allocated == 1):
                        break
                    for k in range(10):
                        # checking if the class room is free
                        if(cr_df[cr_no_index][days[j]][k][0] == 0):
                            # getting the index pf particular teachers tt
                            teacher_sub = df2['Teacher'].where(df2['Subject'] == sub ).dropna()
                            teacher_sub = teacher_sub.iloc[0]
                            dummy_df = teacher.where(teacher['Teacher'] == teacher_sub)
                            dummy_df = dummy_df[pd.notnull(dummy_df['Teacher'])]

                            teacher_no_index = np.where(teacher_list == teacher_sub)[0]
                            teacher_no_index = teacher_no_index.astype(int)
                            teacher_no_index = teacher_no_index[0] 

                            #checking if the teacher is free
                            if(teachers_df[teacher_no_index][days[j]][k][0] == 0):

                                # getting the index of the tt of particular division
                                div_index = np.where(division_list == div)[0]

                                div_index = div_index.astype(int)
                                div_index = div_index[0]

                                #checking if the division is free
                                if(division_df[div_index][days[j]][k][0] == 0 and days_check[j][1] == 0):
                                    #getting the total no. of hours that subject is conducted in a week
                                    hours = df1['hours in week'].where(df1['Subject'] == sub).dropna().iloc[0]

                                    hours = int(hours)
                                    flag_break = 0
                                    if(hours > 2):
                                        hours = 2

                                    dummy_df1 = cr_df[cr_no_index].copy()
                                    dummy_df2 = teachers_df[teacher_no_index].copy()
                                    dummy_df3 = division_df[div_index].copy()
                                    try:
                                        for z in range(2):

                                            if(dummy_df1.iloc[k+z,j][0] != 0):
                                                flag_break = 1
                                            if(dummy_df2.iloc[k+z,j][0] != 0):
                                                flag_break = 1
                                            if(dummy_df3.iloc[k+z,j][0] != 0):
                                                flag_break = 1 
                                    except:
                                        flag_break = 1

                                    if(flag_break == 1):
                                        break

                                    # allocating the lecture in all the time tables
                                    for z in range(int(hours)):

                                        cr_df[cr_no_index].iat[k+z,j] = [1,div +" "+ sub]

                                        teachers_df[teacher_no_index].iat[k+z,j] = [1,div+" "+ sub]


                                        division_df[div_index].iat[k+z,j] = [1,sub]

                                    #trying to allocate lunch to the division if the time is right
                                    lunch = 0
                                    try:
                                        current = division_df[div_index].index[k+hours]

                                        lunch = lunch_break('11:00 AM','5:00 PM',current)



                                    except:
                                        pass

                                    # trying to give a break to the teacher
                                    try:
                                        teachers_df[teacher_no_index].iat[k+hours,j] = [1,'break']

                                        if(days_check[j][2] == 0):
                                            if(lunch == 1):
                                                if(division_df[div_index].iloc[k+hours,j][0] == 0):
                                                    days_check[j][2] = 1
                                                    division_df[div_index].iat[k+hours,j] = [1,'lunch break']
                                    except:

                                        pass

                                    #subtracting the hours from the df1
                                    df1['hours in week'][df1['hours in week'].where(df1['Subject'] == sub).dropna().index[0]] = df1['hours in week'][df1['hours in week'].where(df1['Subject'] == sub).dropna().index[0]] - hours

                                    # checking whetehr the maximum limit to the no. of lectures in a day has been reached or not
                                    div_hour = 0
                                    #changes
                                    for z in range(len(division_df[div_index])):
                                        dummy_var = division_df[div_index].iloc[:,j][z][0]
                                        if(dummy_var != 0):
                                            dummy_var = 1
                                        div_hour = div_hour + dummy_var
                                    if(div_hour>=div_max_limit):
                                        days_check[j][1] = 1   



                                    #checkking whether the subject hours have been completed
                                    #checking whether all the subjects of the division have been completed or not
                                    if(df1['hours in week'].where(df1['Subject'] == sub).dropna().reset_index(drop=True)[0] == 0):
                                        df1['completed'][df1['hours in week'].where(df1['Subject'] == sub).dropna().index[0]] = 1
                                        lec_allocated = 1
                                        div_not_completed = 0
                                        for z in range(len(df1)):
                                            if(df1['completed'][z] == 0):
                                                div_not_completed = 1
                                        if(div_not_completed == 0):
                                            flag_div_completed = 1


                                        break
                                    else:
                                        lec_allocated = 1
                                        break



                                else:
                                    continue



                            else:
                                continue

                        else:
                            continue


            else:
                # subject is a practical and will be conducted in a particular lab
                cr_div = dummy_df['cr'].iloc[0]
                cr_no_index = np.where(cr_list == cr_div)[0]
                cr_no_index = cr_no_index.astype(int)
                cr_no_index = cr_no_index[0]
                if(df1['completed'].iloc[i] == 0):
                    lec_allocated = 0
                for j in range(7):

                    if(lec_allocated == 1):
                        break
                    for k in range(10):

                        if(cr_df[cr_no_index][days[j]][k][0] == 0):
                            # getting the index pf particular teachers tt
                            teacher_sub = df2['Teacher'].where(df2['Subject'] == sub ).dropna()
                            teacher_sub = teacher_sub.iloc[0]
                            dummy_df = teacher.where(teacher['Teacher'] == teacher_sub)
                            dummy_df = dummy_df[pd.notnull(dummy_df['Teacher'])]

                            teacher_no_index = np.where(teacher_list == teacher_sub)[0]
                            #
                            teacher_no_index = teacher_no_index.astype(int)
                            teacher_no_index = teacher_no_index[0] 
                            if(teachers_df[teacher_no_index][days[j]][k][0] == 0):

                                # getting the index of the tt of particular division
                                div_index = np.where(division_list == div)[0]
                                #
                                div_index = div_index.astype(int)
                                div_index = div_index[0]
                                if(division_df[div_index][days[j]][k][0] == 0 and days_check[j][1] == 0):
                                    #getting the total no. of hours that subject is conducted in a week
                                    hours = df1['hours in week'].where(df1['Subject'] == sub).dropna().iloc[0]

                                    hours = int(hours)
                                    flag_break = 0
                                    if(hours > 2):
                                        hours = 2

                                    dummy_df1 = cr_df[cr_no_index].copy()
                                    dummy_df2 = teachers_df[teacher_no_index].copy()
                                    dummy_df3 = division_df[div_index].copy()
                                    try:
                                        for z in range(2):


                                            if(dummy_df1.iloc[k+z,j][0] != 0):
                                                flag_break = 1
                                            if(dummy_df2.iloc[k+z,j][0] != 0):
                                                flag_break = 1
                                            if(dummy_df3.iloc[k+z,j][0] != 0):
                                                flag_break = 1 
                                    except:
                                        flag_break = 1


                                    if(flag_break == 1):
                                        break



                                    for z in range(int(hours)):

                                        cr_df[cr_no_index].iat[k+z,j] = [1,div+" "+ sub]

                                        teachers_df[teacher_no_index].iat[k+z,j] = [1,div+" "+ sub]


                                        division_df[div_index].iat[k+z,j] = [1,sub]

                                    lunch = 0

                                    try:
                                        current = division_df[div_index].index[k+hours]

                                        lunch = lunch_break('11:00 AM','4:00 PM',current)



                                    except:
                                        pass

                                    try:
                                        teachers_df[teacher_no_index].iat[k+hours,j] = [1,'break']
                                        if(days_check[j][2] == 0):
                                            if(lunch == 1):

                                                if(division_df[div_index].iloc[k+hours,j][0] == 0):
                                                    days_check[j][2] = 1
                                                    division_df[div_index].iat[k+hours,j] = [1,'lunch break']
                                    except:

                                        pass


                                    df1['hours in week'][df1['hours in week'].where(df1['Subject'] == sub).dropna().index[0]] = df1['hours in week'][df1['hours in week'].where(df1['Subject'] == sub).dropna().index[0]] - hours

                                    div_hour = 0
                                    #changes
                                    for z in range(len(division_df[div_index])):
                                        dummy_var = division_df[div_index].iloc[:,j][z][0]
                                        if(dummy_var != 0):
                                            dummy_var = 1
                                        div_hour = div_hour + dummy_var
                                    if(div_hour>=div_max_limit):
                                        days_check[j][1] = 1



                                    if(df1['hours in week'].where(df1['Subject'] == sub).dropna().reset_index(drop=True)[0] == 0):
                                        df1['completed'][df1['hours in week'].where(df1['Subject'] == sub).dropna().index[0]] = 1
                                        lec_allocated = 1
                                        div_not_completed = 0
                                        for z in range(len(df1)):
                                            if(df1['completed'][z] == 0):
                                                div_not_completed = 1
                                        if(div_not_completed == 0):
                                            flag_div_completed = 1


                                        break
                                    else:
                                        lec_allocated = 1
                                        break



                                else:
                                    continue



                            else:
                                continue

                        else:
                            continue
            i = i+1            
            if(i>= len(df1)):
                i = 0
        
        


    # In[ ]:


    mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="aitt"
        )

    mycursor = mydb.cursor()


    # In[ ]:


    #creating a table for storing divisions timetable
    mycursor.execute("CREATE TABLE IF NOT EXISTS Division_tt (division VARCHAR(255), timeslot VARCHAR(255),  Monday VARCHAR(255), Tuesday VARCHAR(255),  Wednesday VARCHAR(255),  Thursday VARCHAR(255),  Friday VARCHAR(255),  Saturday VARCHAR(255))")

    #retrieving data from the data frames and storing into list
    divi = []
    timeslot = []
    Monday = []
    Tuesday = []
    Wednesday = []
    Thursday = []
    Friday = []
    Saturday = []
    for j in range(len(division_list)):
        div = division_list[j]
        
        for i in range(len(division_df[j])):
            timeslot.append(division_df[j].index[i])
            Monday.append(division_df[j]['Monday'][i][1])
            Tuesday.append(division_df[j]['Tuesday'][i][1])
            Wednesday.append(division_df[j]['Wednesday'][i][1])
            Thursday.append(division_df[j]['Thursday'][i][1])
            Friday.append(division_df[j]['Friday'][i][1])
            Saturday.append(division_df[j]['Saturday'][i][1])
            divi.append(div)

    #storing the data in tuple form        
    val = []
    for i in range(len(divi)):
        dummy = (divi[i], timeslot[i], Monday[i], Tuesday[i], Wednesday[i], Thursday[i], Friday[i], Saturday[i])
        val.append(dummy)

    #sql line for inserting the row into the table    
    sql = "INSERT INTO Division_tt (division, timeslot, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

    #executing the statement

    mycursor.executemany(sql, val)

    mydb.commit()


    # In[ ]:


    #creating a table for storing teachers timetable
    mycursor.execute("CREATE TABLE IF NOT EXISTS Teachers_tt (teacher VARCHAR(255), timeslot VARCHAR(255),  Monday VARCHAR(255), Tuesday VARCHAR(255),  Wednesday VARCHAR(255),  Thursday VARCHAR(255),  Friday VARCHAR(255),  Saturday VARCHAR(255))")

    #retrieving data from the data frames and storing into list
    teach = []
    timeslot = []
    Monday = []
    Tuesday = []
    Wednesday = []
    Thursday = []
    Friday = []
    Saturday = []
    for j in range(len(teacher_list)):
        t = teacher_list[j]
        
        for i in range(len(teachers_df[j])):
            timeslot.append(teachers_df[j].index[i])
            Monday.append(teachers_df[j]['Monday'][i][1])
            Tuesday.append(teachers_df[j]['Tuesday'][i][1])
            Wednesday.append(teachers_df[j]['Wednesday'][i][1])
            Thursday.append(teachers_df[j]['Thursday'][i][1])
            Friday.append(teachers_df[j]['Friday'][i][1])
            Saturday.append(teachers_df[j]['Saturday'][i][1])
            teach.append(t)

    #storing the data in tuple form        
    val = []
    for i in range(len(teach)):
        dummy = (teach[i], timeslot[i], Monday[i], Tuesday[i], Wednesday[i], Thursday[i], Friday[i], Saturday[i])
        val.append(dummy)

    #sql line for inserting the row into the table    
    sql = "INSERT INTO Teachers_tt (teacher, timeslot, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

    #executing the statement

    mycursor.executemany(sql, val)

    mydb.commit()


    # In[ ]:


    #creating a table for storing teachers timetable
    mycursor.execute("CREATE TABLE IF NOT EXISTS CR_tt (CR VARCHAR(255), timeslot VARCHAR(255),  Monday VARCHAR(255), Tuesday VARCHAR(255),  Wednesday VARCHAR(255),  Thursday VARCHAR(255),  Friday VARCHAR(255),  Saturday VARCHAR(255))")

    #retrieving data from the data frames and storing into list
    crs = []
    timeslot = []
    Monday = []
    Tuesday = []
    Wednesday = []
    Thursday = []
    Friday = []
    Saturday = []
    for j in range(len(cr_list)):
        c = cr_list[j]
        
        for i in range(len(cr_df[j])):
            timeslot.append(cr_df[j].index[i])
            Monday.append(cr_df[j]['Monday'][i][1])
            Tuesday.append(cr_df[j]['Tuesday'][i][1])
            Wednesday.append(cr_df[j]['Wednesday'][i][1])
            Thursday.append(cr_df[j]['Thursday'][i][1])
            Friday.append(cr_df[j]['Friday'][i][1])
            Saturday.append(cr_df[j]['Saturday'][i][1])
            crs.append(c)

    #storing the data in tuple form        
    val = []
    for i in range(len(crs)):
        dummy = (crs[i], timeslot[i], Monday[i], Tuesday[i], Wednesday[i], Thursday[i], Friday[i], Saturday[i])
        val.append(dummy)

    #sql line for inserting the row into the table    
    sql = "INSERT INTO CR_tt (CR, timeslot, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

    #executing the statement

    mycursor.executemany(sql, val)

    mydb.commit()



    return HttpResponse("success")