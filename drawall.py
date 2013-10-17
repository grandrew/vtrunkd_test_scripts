#!/usr/bin/python
import os,commands 
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
import cgi
import cgitb
cgitb.enable()
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import sys, json
import sys, time, glob, os, numpy, datetime
import matplotlib.pyplot as plt
import colorsys

def parse_str(ss):
    l_json = []
    for l in ss.split("\n"):
        dl = l.split();
        if len(l) < 5: continue
        try:
            sdtime = dl[2];
            dt = time.strptime("14/09/12 %s000" % sdtime, '%d/%m/%y %H:%M:%S.%f');
        except:
            raise ValueError("Could not parse date: \n%s\nwith:\n%s" % (l, repr(l.split(" "))))
            sys.exit()
        ms = int(sdtime.split(".")[1])
        t = int(time.mktime(dt))*1000+ms
        data = json.loads('{' + l.split('{')[1])
        data["ts"] = t
        l_json.append(data)
    return l_json

def toilet(filename):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in filename if c in valid_chars)


def main():
    form = cgi.FieldStorage()
    if not "session" in form:
        print "Content-type: text/html\n"
        print """<html><body>No input session given</body></html>"""
        sys.exit()
    session=toilet(form["session"].value)
    l=int(form["length"].value)
    if len(session) < 5 or len(session) > 16:
        sys.exit()
 
    
    # now prepare logfile
    jsons=commands.getoutput("tail -n 10000 /var/log/syslog | grep '%s' | grep '{' | tail -n %s" % (session, str(l)))
    data_srv = parse_str(jsons)
    # now plot
    try:
        plot_data("/tmp/plot_%s.png" % session, None, data_srv, session)
    except ValueError:
        plot_data("/tmp/plot_%s.png" % session, None, data_srv, session, False)

def unused():
    data_cli_arr=[]
    data_srv_arr=[]
    someName = ""
    for jsonLine in data_cli:
        if len(data_cli_arr) == 0:
            data_cli_arr_item = []
            data_cli_arr_item.append(jsonLine)
            data_cli_arr.append(data_cli_arr_item)
        else:
            succ=0
            for someArr in data_cli_arr:
                if someArr[0]['name'] == jsonLine['name']:
                    someArr.append(jsonLine)
                    succ = 1
                    break
            if succ == 1:
                continue
            data_cli_arr_item = []
            data_cli_arr_item.append(jsonLine)
            data_cli_arr.append(data_cli_arr_item)
    DNAME='incomplete_seq_len'
    plotAX2 = plt.subplot(515)
    plt.title(DNAME + " (client)")
    plt.plot(zipj(data_cli_arr[0], "ts"), zipj(data_cli_arr[0], 'isl'), "-")



# name send_q_limit send_q rtt my_rtt cwnd isl buf_len upload hold_mode ACS R_MODE
def plot_data(fn, data_cli, data_srv, session, logax=True):
    
    data_srv_arr=[]
    someName = ""    
    for jsonLine in data_srv:
        if len(data_srv_arr) == 0:
            data_srv_arr_item = []
            data_srv_arr_item.append(jsonLine)
            data_srv_arr.append(data_srv_arr_item)
        else:
            succ=0
            for someArr in data_srv_arr:
                if someArr[0]['name'] == jsonLine['name']:
                    someArr.append(jsonLine)
                    succ = 1
                    break
            if succ == 1:
                continue
            data_srv_arr_item = []
            data_srv_arr_item.append(jsonLine)
            data_srv_arr.append(data_srv_arr_item)
            
    figurePlot = plt.figure(figsize=(23.5, 4.5 * 1))
    figurePlot.text(.5, .95, session, horizontalalignment='center', size=20)

    plotAX3 = plt.subplot(111)
    #if logax: plotAX3.set_yscale('log')
    i=0
    for someLine in data_srv_arr:
        plt.plot(zipj(data_srv_arr[i], "ts"), zipj(data_srv_arr[i], "s_r_m"), "--", label='speed_garbage '+data_srv_arr[i][0]['name'],c=tohex(*(colorsys.hsv_to_rgb((1./6)*(i),1,1))))
        plt.plot(zipj(data_srv_arr[i], "ts"), zipj(data_srv_arr[i], "s_r"), "*", label='speed_resend '+data_srv_arr[i][0]['name'],c=tohex(*(colorsys.hsv_to_rgb((1./6)*(i),1,0.8))))
        plt.plot(zipj(data_srv_arr[i], "ts"), zipj(data_srv_arr[i], "s_e"), "-", label='speed_eff '+data_srv_arr[i][0]['name'],c=tohex(*(colorsys.hsv_to_rgb((1./6)*(i),1,0.6))))
        plt.legend(bbox_to_anchor=(0, 1), loc=2, borderaxespad=0.)
        i= i+1
    ymin,ymax = plt.ylim()
    ic = 999999
    for data_arr in data_srv_arr:
        if ic % 11 == 1: ic -= 2
        for json in data_arr:
            if json["R_MODE"] == 2:
                plt.annotate(json['name'], xy=(int(json['ts']), int(0)),  xycoords='data', xytext=(int(json['ts']), (ymax/10.0)*float(ic % 10)), textcoords='data', arrowprops=dict(facecolor='red', shrink=0.05),  horizontalalignment='right', verticalalignment='top', size=16)
                ic -= 1
            if json["R_MODE"] == 3:
                plt.annotate(json['name'], xy=(int(json['ts']), int(0)),  xycoords='data', xytext=(int(json['ts']), (ymax/10.0)*float(ic % 10)), textcoords='data', arrowprops=dict(facecolor='green', shrink=0.05),  horizontalalignment='right', verticalalignment='top', size=16)
                ic -= 1


    #DNAME="buf_len"    
    #i=0
    #try:
    #    plt.plot(zipj(data_srv_arr[0], "ts"), zipj(data_srv_arr[0], 'buf_len'), "-")
    #    plt.plot(zipj(data_srv_arr[0], "ts"), numpy.array(zipj(data_srv_arr[0], 'a_r_f'))*20, ".", label="ag ready flag" )
    #except IndexError:
    #    pass
    #for someLine in data_srv_arr:
    #    plt.plot(zipj(data_srv_arr[i], "ts"), numpy.array(zipj(data_srv_arr[i], "hold_mode"))*((i*10)+90), ".", label="hold_mode "+data_srv_arr[i][0]['name'])
    #    plt.plot(zipj(data_srv_arr[i], "ts"), numpy.array(zipj(data_srv_arr[i], "R_MODE"))*((i*10)+30), ".", label="R_MODE "+data_srv_arr[i][0]['name'])
	#plt.legend(bbox_to_anchor=(0, 1), loc=2, borderaxespad=0.)
    #    i=i+1
    
    
    figurePlot.savefig(fn, dpi=35, bbox_inches='tight')
    print "Content-type: image/png\n"
    print file(fn).read()
    
def zipj(l_json, name):
    d = []
    for j in l_json:
        d.append(j[name])
    return d


# NOT FINISHED
def zip_sum(ll_json, name):
    # create main grid
    # get minimal ts,maximum ts from all jsons
    # TODO: finish this!:
    ts_start = ll_json[0][0]["ts"]
    ts_end = ll_json[0][-1]["ts"]
    # generate even grid
    mgrid = np.mgrid[1:0.9:201j]
    
    # now interpolate to grid for each json
    for ld in ll_json[1:]:
        l_data = zipj(ld, name)
        l_ts = zipj(ld, "ts")
        for d in ld:
            z2 = scipy.interpolate.griddata((x.ravel(), y.ravel()), z.ravel(), (x2, y2), method='linear')

def tohex(r,g,b):
	hexchars = "0123456789ABCDEF"
	r = int(r * 255)
	g = int(g * 255)
	b = int(b * 255)
	return "#" + hexchars[r / 16] + hexchars[r % 16] + hexchars[g / 16] + hexchars[g % 16] + hexchars[b / 16] + hexchars[b % 16]


if __name__ == '__main__':
    main()