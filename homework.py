import copy
import time
def convert_to_cnf(s):
	#print "QUESTION", s
	if '=>' in s:
		s = eliminate_implication(s)
	else:
		stack = []
		for char in s:
			stack.append(char)
		stack = [value for value in stack if value != ' ']
		s = ''.join(stack)
	if '~' in s:
		s = move_negation(s)
	if s[0] == '(':
		s = s[1:-1]
	lst = distribute(s)
	return lst

def find_main_operator(string):
	br = 0
	main_op = ''
	ind = 0
	for i, char in enumerate(string):
		if char == "(":
			br += 1
		elif char == ')':
			br -=1
		elif char in ['&','|']:
			if br == 0:
				ind = i
				main_op = char
	return ind, main_op

def find_operand(string, ind):
	if string[0] == '(':
		left = string[1:ind-1]
	else:
		left = string[:ind]
	if string[ind+1] == '(':
		right = string[ind+2:-1]
	else:
		right = string[ind+1:]
	return left, right

def distribute(string):
	lst = []
	if '&' in string and '|' in string:
		ind, op = find_main_operator(string)
		left, right = find_operand(string, ind)
		if op == '&':
			lst.extend(distribute(left))
 			lst.extend(distribute(right))
 		if op == '|':
 			ll = ''
 			lr = ''
 			rl = ''
 			rr = ''
 			l_op = ''
 			r_op = ''
 			if '&' in left or '|' in left:
 				l_i,l_op = find_main_operator(left)
 				ll,lr = find_operand(left, l_i)
 			if '&' in right or '|' in right:
 				r_i, r_op = find_main_operator(right)
 				rl,rr = find_operand(right, r_i)
 			# print ll, lr, rl, rr
			if l_op == '&' and r_op != '&':
				s = '('+ll+'|'+right+')&('+lr+'|'+right+')'
				lst.extend(distribute(s))
			elif r_op == '&' and l_op != '&':
				s = '('+left+'|'+rl+')&('+left+'|'+rr+')'
				lst.extend(distribute(s))
			elif l_op == '&' and r_op == "&":
				s = '('+ll+'|'+right+')&('+lr+'|'+right+')'
				lst.extend(distribute(s))

	elif '&' in string:
		ind, op = find_main_operator(string)
		left, right = find_operand(string, ind)
		lst.extend(distribute(left))
		lst.extend(distribute(right))
 	else :
 		lst.append(string)
 	return lst

def move_inwards(string):
	if string[1] == '~':
		return string[2:-1]
	elif '&' in string or '|' in string:
		s = string[1:-1]
		ind, sym = find_main_operator(s)
		a = s[:ind]
		b = s[ind+1:]
		a = '(~'+a+')'
		b = '(~'+b+')'
		ret_a = move_negation(a)
		ret_b = move_negation(b)
		if '&' == sym:
			return '('+ret_a + '|' + ret_b +')'
		elif '|' == sym:
			return '('+ret_a + '&' + ret_b +')' 
	return '(~'+string+')'

def move_negation(s):
	stack = []
	for char in s:
		if char ==')':
			temp = [')']
			c = stack.pop()
			while c != '(' :
				temp.append(c)
				c = stack.pop()
			temp.append('(')
			string = ''.join(temp[::-1])
			if string[1] == '~':
				if '|' in string:
					stack.append(move_inwards(string[2:-1]))
				elif '&' in string:
					stack.append(move_inwards(string[2:-1]))
				elif '~' == string[3]:
					stack.append(move_inwards(string[2:-1]))
				else:
					stack.append(string)	
			else:
				stack.append(string)

		else:
			stack.append(char)
			stack = [value for value in stack if value != ' ']
	return stack[0]

def eliminate_implication(s):
	stack = []
	for char in s:
		if char ==')':
			#print stack
			temp = [')']
			c = stack.pop()
			while c != '(' :
				temp.append(c)
				c = stack.pop()
			temp.append('(')
			#print ''.join(temp[::-1])
			string = ''.join(temp[::-1])
			if '=>' in string:
				i = string.index('=')
				j = i+1
				a = string[1:i]
				b = string[j+1:-1]
				operand = "((~"+a+')|'+b+")"
				stack.append(operand)
			else:
				stack.append(string)
			#then pop till (
		else:
			stack.append(char)
			stack = [value for value in stack if value != ' ']
	return stack[0]

def find_args(string):
	lst = string.partition('(')
	op = lst[0]
	args = lst[-1].rpartition(')')[0]
	args = args.split(',')
	args = [i.strip() for i in args]
	return op, args

def is_variable(x):
    if isinstance(x,str):
        return x.islower()
    return False

def add_theta(theta, var, val):
    s2 = theta.copy()
    s2[var] = val
    return s2

def is_compound(x):
	if isinstance(x,str):
		if '(' in x:
			return True
	return False

def unify(x, y, theta):
	#check if negation symbol
	if theta is None:
		return None
	elif x==y:
		return theta
	elif is_variable(x):
		return unify_var(x, y, theta)
	elif is_variable(y):
		return unify_var(y, x, theta)
	elif is_compound(x) and is_compound(y):
		x_op, x_args = find_args(x)
		y_op, y_args = find_args(y)
		return unify(x_args, y_args, unify(x_op, y_op, theta))
	elif isinstance(x, list) and isinstance(y, list) and len(x)==len(y):
		return unify(x[1:], y[1:], unify(x[0], y[0], theta))
	else:
		return None

def unify_var(var, x, theta):
    if var in theta:
    	return unify(theta[var], x, theta)
    elif x in theta:
        return unify(var,theta[x],theta)
    else:
        return add_theta(theta, var, x)

def resolution(KB, query):
	if query in KB:
		return True
	# print query
	if '~' in query:
		query = query.replace('~','')
	else:
		query = '~'+query
	#print query
	KB.append(query)
	new = set()
	prev = 0
	start = time.time()
	while True:
		n = len(KB)
		if prev == 0:
			pairs = [(KB[i], KB[j]) for i in range(n) for j in range(i+1,n)]
		else:
			pairs = [(KB[i], KB[j]) for i in range(n) for j in range(prev,n)]
		prev = n
		for (ci, cj) in pairs:
			# print ci
			# print cj
			resolvents = resolve(ci,cj)
			# print str(ci), "+", str(cj) + ":    " +    str(resolvents)
			if False in resolvents:
				return True
			new.update(set(resolvents))
			end = time.time()
			if (end-start) >= 50:
				return False

		if new.issubset(set(KB)):
			return False
		for c in new:
			if c not in KB:
				KB.append(c)
		new = set()

def resolve(ci, cj):
	ci_lst = split_or(ci)
	cj_lst = split_or(cj)
	resolve_clauses = []
	resolvent = []
	resolve_clauses.extend(ci_lst)
	resolve_clauses.extend(cj_lst)
	flag = False
	for i in ci_lst:
		for j in cj_lst:
			if ('~' in i and '~' not in j) or ('~' in j and '~' not in i):
				theta = unify(i.replace('~',''), j.replace('~',''), {})
				if theta is not None:
					flag = True
					clauses = copy.copy(resolve_clauses)
					clauses.remove(i)
					clauses.remove(j)
					clauses = subst(theta, clauses)
					clauses = list(set(clauses))
					caluses = sorted(clauses)
					c = '|'.join(clauses)
					resolvent.append(c)
	if flag and '' in resolvent:
		return [False]
	else:
		return resolvent
	# if len(resolve_clauses) == len(ci) + len(cj):
	# 	return []
	# elif len(resolve_clauses) == 0:
	# 	return [False]
	# else:
	# 	return resolve_clauses

def subst(theta, clauses):
	for j, clause in enumerate(clauses):
		op, args = find_args(clause)
		for i, arg in enumerate(args):
			if arg in theta:
				arg = theta[arg]
			args[i] = arg
		clauses[j] = op+'('+','.join(args)+')'
	return clauses
			
def split_or(string):
	ret_lst = []
	if '|' in string:
	 	ind, op = find_main_operator(string)
	 	left, right = find_operand(string,ind)
		ret_lst.extend(split_or(left))
		ret_lst.extend(split_or(right)) 	
	# 	lst = [string[:ind], string[ind+1:]]
	# 	for i in lst:
	# 		ret_lst.extend(split_or(i))
	else:
		ret_lst.append(string)
	return ret_lst		

def remove_space(string):
	stack = []
	for c in query:
		stack.append(c)
	stack = [value for value in stack if value != ' ']
	s = ''.join(stack)
	return s

if __name__ == "__main__":
    f=open("input.txt",'r')
    f1 = open("output.txt",'w')
    s = f.read()
    inp_lst = s.split('\n')
    #print inp_lst
    query_len = int(inp_lst[0])
    kb_len = int(inp_lst[query_len+1])
    query_lst = inp_lst[1:query_len+1]
    KB_lst = inp_lst[int(inp_lst[0])+2:int(inp_lst[0])+2+kb_len]
    # print KB_lst
    KB_cnf = []
    for i,j in enumerate(KB_lst):
    	lst = convert_to_cnf(j)
    	# print lst
    	for h, k in enumerate(lst):
    		split_lst = split_or(k)
    		for z,literal in enumerate(split_lst):
    			op, args = find_args(literal)
    			for arg in args:
    				if is_variable(arg):
    					ind = args.index(arg) 
    					arg = arg + str(i)
    					args[ind] = arg
    			split_lst[z] = op +'('+ ','.join(args)+')'
    		split_lst = sorted(split_lst)
    		lst[h] = '|'.join(split_lst)
    	KB_cnf.extend(lst)
    #print KB_cnf
    for i, query in enumerate(query_lst):
		query_lst[i] = remove_space(query)
    #print query_lst
	# convert_to_cnf('(A=>B)')
    # convert_to_cnf('(~(~(A|B)))')
    # convert_to_cnf('(~(~A))')
    # convert_to_cnf('(~((~A)|B))')
    # convert_to_cnf('((A(x)=>B(x))=>C)')
    # convert_to_cnf('(~(~A))')	
    # sentence = "(~(~((~A(x))&(~B(x,y)))))"
    # convert_to_cnf(sentence)
    # sentence = "(~((~A(x))&(~B(x,y))))"
    # convert_to_cnf(sentence)
    # sentence = "(~(~A(x)))"
    # convert_to_cnf(sentence)
    # sentence = "((~((~A)|B))|C)"
    # convert_to_cnf(sentence)
    # sentence = "((~(D(x,y) & Q(y)))|C(x,y))"
    # convert_to_cnf(sentence)
    # convert_to_cnf('(~((B|C)&(D|E)))')
    # convert_to_cnf("((A&B)|(C&D))")
    # distribute('(~A(x))')
    # distribute('(~B(x,y))')
    # distribute('(A&(~B))')
    # print resolve('A(x1)|B(x1)|C(x1)', '~B(x2)|~C(x2)')
    for query in query_lst:
    	CNF_KB = copy.copy(KB_cnf)
    	val = resolution(CNF_KB, query)
    	f1.write(str(val).upper()+'\n')
    	print val
    f.close()
    f1.close()
    
    #print convert_to_cnf('(A(x)&(B(x)&(C(x)|D(x))))')
    #print convert_to_cnf('(AnimalLover(x) & (Animal(y) & Kills(x,y)))')
    #print resolve("A(x)", "~A(x)")
	# theta = unify('B(x1)','B(x2)', {})
    # print theta
    # print resolution(['A(x1)|~B(x1)', 'B(x2)'],'A(Bob)')
    # print(resolution(KB_cnf, 'H(John)'))
    # print move_negation('((~(((American(x)&Weapon(y))&Sells(x,y,z))&Hostile(z)))|Criminal(x))')
    #print move_negation('(~(A&B))')
    # print split_or('((~B(x,y))|(~C(x,y)))|A(x)')