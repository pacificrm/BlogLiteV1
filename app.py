from os import path
from flask import Flask , render_template,request,redirect,flash
from modals import db,Users,Blogs,Profile,Follow,Comments,Likes,Dislikes
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,login_user,logout_user,current_user,login_required
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# from werkzeug.utils import secure_filename

UPLOAD_BLOG = 'static/blogs'
UPLOAD_PROFILE= 'static/profile'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}



# from flask_security import Security,SQLAlchemySessionUserDatastore,login_required
app= Flask(__name__)

cd= path.abspath(path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+path.join(cd,"database.sqlite3")

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SECRET_KEY']="hbvjhfvbjhevbnkvdf"
app.config['UPLOAD_BLOG'] = UPLOAD_BLOG
app.config['UPLOAD_PROFILE'] = UPLOAD_PROFILE


# app.config['SECURITY_PASSWORD_HASH']='bcrypt'
# app.config['SECURITY_PASSWORD_SALT']="supe_secrete_ekdum"
# app.config['SECURITY_REGISTERABLE']=True
# app.config['SECURITY_SEND_REGISTER_EMAIL']=False
# app.config['SECURITY_UNAUTHORIZED_VIEW']=None

# user_security=SQLAlchemySessionUserDatastore(db.session,Users,Role)
# Security(app,user_security)

db.init_app(app)

login_manager=LoginManager()
login_manager.login_view = 'siglog'
login_manager.init_app(app)
login_manager.login_message_category = "danger"

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


# @login_manager.user_loader
# def load_user(user_id):
#     return Users.query.get(user_id)


@app.before_first_request
def create():
    if not path.exists('sqlite:///database.sqlite3'):
        db.create_all()



#     <--------------------------      SARTING PAGE    ---------------------------->

@app.route('/')
def start():
    # return render_template('start.html')
    return render_template('start.html')

# <----------------------------    SIGNUP - LOGIN  PAGE --------------------------------->

@app.route('/signup_login', methods=['GET','POST'])
def siglog():
    if request.method =="POST":
        logmail=request.form.get("login_mail")
        sigmail=request.form.get('signup_mail')

        if not logmail and sigmail :
            signm=request.form.get('user_nm')
            sigpswd1=request.form.get('signup_pswd1')
            sigpswd2=request.form.get('signup_pswd2')
            check=Users.query.filter_by(email=sigmail).first()
            check2=Users.query.filter_by(user_name=signm).first()
            if check==None:
                if len(signm)<3:
                    flash("Use ID must be at least 3 characters !!",category="danger")
                elif (check2):
                    flash("User Name already exists!! Try new.",category="danger")
                elif len(sigmail)<6:
                    flash("Email must be greater than 5 characters !!",category="danger")
                elif len(sigpswd1)<8:
                    flash("Password must be greater than 7 characters !!",category="danger")
                elif (sigpswd1!=sigpswd2):
                    flash("Password didn't matched !!",category="danger")
                else:
                    user=Users(user_name=signm,email=sigmail,password=generate_password_hash(sigpswd1, method = "sha256"))
                    db.session.add(user)
                    db.session.commit()
                    flash("User added successfully, Now login to Cotinue.!!",category="success")
            else:
                flash("User already exists !!",category="danger")

        if not sigmail and logmail:
            logpswd=request.form.get('login_pswd')
            check=Users.query.filter_by(email=logmail).first()
            if check==None:
                flash("User don't exists !! Please Signup to continue board.",category="danger")
            elif not check_password_hash(check.password, logpswd ):
                flash("Wrong password!! Try again.", category="danger")
            else:
                login_user(check,remember=True)
                return redirect("/user/home")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/signup_login")


@app.route('/user/home')
@login_required
def userHome():
    chk=Users.query.filter_by(id=current_user.id).first()
    ck=chk.followed.all()
    blgs=''
    if ck:
        blgs=Blogs.query.filter(Blogs.user_id.in_([c.followed_id for c in ck])).order_by(Blogs.Blog_time.desc()).all()
        print(blgs)
        if len(blgs)>5:
            blgs=blgs[:5]
    return render_template("recentPosts.html",blgs=blgs,ck=ck)

@app.route('/delete/user')
@login_required
def deluser():
    Likes.query.filter_by(user_name=current_user.user_name).delete()
    Dislikes.query.filter_by(user_name=current_user.user_name).delete()
    Comments.query.filter_by(user_name=current_user.user_name).delete()
    Blogs.query.filter_by(user_id=current_user.id).delete()
    Profile.query.filter_by(user_id=current_user.id).delete()
    Users.query.filter_by(id=current_user.id).delete()
    Follow.query.filter_by(followed_id=current_user.id).delete()
    Follow.query.filter_by(follower_id=current_user.id).delete()
    db.session.commit()
    logout_user()
    return redirect("/signup_login")



@app.route('/profile/<int:id>')
def profile(id):
    chk=Users.query.filter_by(id=id).first()
    ck=Profile.query.filter_by(user_id=id).first()
    blgs=Blogs.query.filter_by(user_name=chk.user_name).order_by(Blogs.Blog_time.desc()).all()
    if not ck :
        profile=Profile(user_id=id)
        db.session.add(profile)
        db.session.commit()
    ps=Profile.query.filter_by(user_id=id).first()
    us=Users.query.filter_by(id=id).first()
    return render_template("profile.html",blgs=blgs,id=id,dp=ps.profile_img,tp=ps.totalposts,flwr=us.followers.count(),flwng=us.followed.count(),fn=ps.fullname,ab=ps.about,unm=us.user_name)

@app.route('/user/editProfile',methods=['GET','POST'])
@login_required
def editPofile():
    p=Profile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        fn= request.form.get('fullname')
        ab= request.form.get('about')
        dp=request.files['dp']
        dpname='no-profile-pic.jpeg'
        if dp:
            dpname="{cu}.jpeg".format(cu=current_user.user_name)
            dp.save(path.join(UPLOAD_PROFILE, dpname))
            Profile.query.filter_by(user_id=current_user.id).update(dict(fullname=fn,about=ab,profile_img=dpname))
            db.session.commit()
            return redirect("/profile/{cu}".format(cu=current_user.id))
        else:
            Profile.query.filter_by(user_id=current_user.id).update(dict(fullname=fn,about=ab))
            db.session.commit()
            return redirect("/profile/{cu}".format(cu=current_user.id))
    return render_template("edit_profile.html" ,em=current_user.email,un=current_user.user_name,fn=p.fullname,ab=p.about)


@app.route('/user/postBlog',methods=['GET','POST'])
@login_required
def postBlog():
    if request.method == 'POST':
        title=request.form.get('blogTitle')
        preview=request.form.get('blogPreview')
        content=request.form.get('blogContent')
        image=request.files['blogImage']
        imgname="no-img.jpeg"
        if image:
            imgname="{cu}{dt}.jpeg".format(cu=current_user.user_name,dt=datetime.now())
            image.save(path.join(UPLOAD_BLOG, imgname))
        bg=Blogs(Blog_title=title,Blog_preview=preview,Blog_content=content,Blog_img=imgname,user_name=current_user.user_name,user_id=current_user.id,Blog_time=datetime.now())
        Profile.query.filter_by(user_id=current_user.id).update(dict(totalposts=Profile.totalposts+1))
        db.session.add(bg)
        db.session.commit()
        return redirect('/profile/{cu}'.format(cu=current_user.id))
    return render_template("postBlog.html")

@app.route('/editBlog/<int:bgid>',methods=['GET','POST'])
@login_required
def editblog(bgid):
    Bg=Blogs.query.filter_by(id=bgid).first()
    if Bg:
        if request.method == 'POST':
            title=request.form.get('blogTitle')
            preview=request.form.get('blogPreview')
            content=request.form.get('blogContent')
            image=request.files['blogImage']
            imgname="no-img.jpeg"
            if image:
                imgname="{cu}{dt}.jpeg".format(cu=current_user.user_name,dt=datetime.now())
                image.save(path.join(UPLOAD_BLOG, imgname))
            Blogs.query.filter_by(id=bgid).update(dict(Blog_title=title,Blog_preview=preview,Blog_content=content,
            Blog_img=imgname,Blog_time=datetime.now()))
            db.session.commit()
            return redirect('/profile/{cu}'.format(cu=current_user.id))
    else:
        return ("Blog has been deleted")

    return render_template("editblog.html",bt=Bg.Blog_title,bp=Bg.Blog_preview,bc=Bg.Blog_content,bgid=bgid)

@app.route('/deleteBlog/<int:bgid>',methods=['GET','POST'])
@login_required
def deleteblog(bgid):
    Profile.query.filter_by(user_id=current_user.id).update(dict(totalposts=Profile.totalposts-1))
    Likes.query.filter_by(blog_id=bgid).delete()
    Dislikes.query.filter_by(blog_id=bgid).delete()
    Comments.query.filter_by(blog_id=bgid).delete()
    Blogs.query.filter_by(id=bgid).delete()
    db.session.commit()
    return redirect("/profile/{cu}".format(cu=current_user.id))

@app.route('/blog/<int:bgid>',methods=['GET','POST'])
@login_required
def blog(bgid):
    blg=Blogs.query.filter_by(id=bgid).first()
    return render_template("blog.html",bgid=bgid,bt=blg.Blog_title,bc=blg.Blog_content)

@app.route('/blogengage/<int:bgid>',methods=['GET','POST'])
@login_required
def blogengage(bgid):
    blg=Blogs.query.filter_by(id=bgid).first()
    x=["Likes","Dislikes",'Comments']
    y=[blg.likes,blg.dislikes,blg.total_comments]
    plt.clf()
    # plt.bar(x, y,color='green')
    plt.plot(x,y,c='r',marker='o')
    plt.ylabel("Frequency", rotation="vertical",fontsize=15 ,c="r")
    plt.xlabel("Post-Engagement" ,c="b")
    plt.grid(axis='both', alpha=0.65)
    plt.title('Post-engagement graph',fontsize=15,c="r")
    plt.yticks([n for n in range(int(max(y))+4)])
    plt.legend('count')
    plt.savefig("./static/test.png")
    p="/static/test.png"
    return render_template("postengage.html",p=p,bgid=bgid)




@app.route('/likeBlog/<int:bgid>',methods=['GET','POST'])
@login_required
def Likeblog(bgid):
    l=Likes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).first()
    dl=Dislikes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).first()
    if l :
        return redirect("/profile/{cu}".format(cu=current_user.id))
    elif dl:
        Dislikes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).delete()
        Blogs.query.filter_by(id=bgid).update(dict(likes=Blogs.likes+1))
        Blogs.query.filter_by(id=bgid).update(dict(dislikes=Blogs.dislikes-1))
        nl=Likes(blog_id=bgid,user_name=current_user.user_name)
        db.session.add(nl)
        db.session.commit()
        return redirect("/profile/{cu}".format(cu=current_user.id))
    else:
        Blogs.query.filter_by(id=bgid).update(dict(likes=Blogs.likes+1))
        nl=Likes(blog_id=bgid,user_name=current_user.user_name)
        db.session.add(nl)
        db.session.commit()
        return redirect("/profile/{cu}".format(cu=current_user.id))


@app.route('/dislikeBlog/<int:bgid>',methods=['GET','POST'])
@login_required
def Dislikeblog(bgid):
    l=Likes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).first()
    dl=Dislikes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).first()
    if dl :
        return redirect("/profile/{cu}".format(cu=current_user.id))
    elif l:
        Likes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).delete()
        Blogs.query.filter_by(id=bgid).update(dict(dislikes=Blogs.dislikes+1))
        Blogs.query.filter_by(id=bgid).update(dict(likes=Blogs.likes-1))
        ndl=Dislikes(blog_id=bgid,user_name=current_user.user_name)
        db.session.add(ndl)
        db.session.commit()
        return redirect("/profile/{cu}".format(cu=current_user.id))
    else:
        Blogs.query.filter_by(id=bgid).update(dict(dislikes=Blogs.dislikes+1))
        ndl=Likes(blog_id=bgid,user_name=current_user.user_name)
        db.session.add(ndl)
        db.session.commit()
        return redirect("/profile/{cu}".format(cu=current_user.id))

@app.route('/hlikeBlog/<int:bgid>',methods=['GET','POST'])
@login_required
def hLikeblog(bgid):
    l=Likes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).first()
    dl=Dislikes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).first()
    if l :
        return redirect("/user/home")
    elif dl:
        Dislikes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).delete()
        Blogs.query.filter_by(id=bgid).update(dict(likes=Blogs.likes+1))
        Blogs.query.filter_by(id=bgid).update(dict(dislikes=Blogs.dislikes-1))
        nl=Likes(blog_id=bgid,user_name=current_user.user_name)
        db.session.add(nl)
        db.session.commit()
        return redirect("/user/home")
    else:
        Blogs.query.filter_by(id=bgid).update(dict(likes=Blogs.likes+1))
        nl=Likes(blog_id=bgid,user_name=current_user.user_name)
        db.session.add(nl)
        db.session.commit()
        return redirect("/user/home")


@app.route('/hdislikeBlog/<int:bgid>',methods=['GET','POST'])
@login_required
def hDislikeblog(bgid):
    l=Likes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).first()
    dl=Dislikes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).first()
    if dl :
        return redirect("/user/home")
    elif l:
        Likes.query.filter_by(blog_id=bgid,user_name=current_user.user_name).delete()
        Blogs.query.filter_by(id=bgid).update(dict(dislikes=Blogs.dislikes+1))
        Blogs.query.filter_by(id=bgid).update(dict(likes=Blogs.likes-1))
        ndl=Dislikes(blog_id=bgid,user_name=current_user.user_name)
        db.session.add(ndl)
        db.session.commit()
        return redirect("/user/home")
    else:
        Blogs.query.filter_by(id=bgid).update(dict(dislikes=Blogs.dislikes+1))
        ndl=Likes(blog_id=bgid,user_name=current_user.user_name)
        db.session.add(ndl)
        db.session.commit()
        return redirect("/user/home")



@app.route('/comment/<int:bgid>',methods=['GET','POST'])
@login_required
def comment(bgid):
    if request.method=='POST':
        cmnt=request.form.get('comment')
        if cmnt :
            bg=Blogs.query.filter_by(id=bgid).first()
            Blogs.query.filter_by(id=bgid).update(dict(total_comments=Blogs.total_comments+1))
            c=Comments(blog_id=bgid,user_name=current_user.user_name,comment=cmnt,comment_time=datetime.now())
            db.session.add(c)
            db.session.commit()
            return redirect("/comment/{bgid}".format(bgid=bgid))
    cm=Comments.query.filter_by(blog_id=bgid).order_by(Comments.comment_time.desc()).all()
    return render_template ("comments.html",cmnts=cm,bc=current_user.id)
            
@app.route('/deletecmn/<int:cmid>',methods=['GET','POST'])
@login_required
def deletecmn(cmid):
    ck=Comments.query.filter_by(id=cmid).first()
    bg=ck.blog_id
    Blogs.query.filter_by(id=bg).update(dict(total_comments=Blogs.total_comments-1))
    Comments.query.filter_by(id=cmid).delete()
    db.session.commit()
    return redirect("/comment/{bg}".format(bg=bg))


@app.route('/search/username', methods=['GET','POST'])
@login_required
def search1():
    if request.method == 'POST':
        fchk=False
        uid=request.form.get('uid')
        if ' ' in uid :
            flash('Enter value without space', category='danger')
        else:
            q='%'+uid+'%'
            lu=Users.query.filter(Users.user_name.like(q)).all()
            if lu:
                return render_template("search.html" ,f=fchk ,lu=lu)
            else:
                flash('No users found !!',category='danger')
    
    return render_template("search.html")

@app.route('/search/fullname', methods=['GET','POST'])
@login_required
def search2():
    fchk=True
    if request.method == 'POST':
        uid=request.form.get('uid')
        if ' ' in uid :
            flash('Enter value without space', category='danger')
        else:
            # pck=Profile.query.filter_by(user_id=current_user.id).first()
            # if pck.fullname :
            q='%'+uid+'%'
            l=Profile.query.filter(Profile.fullname.like(q)).all()
            if l:
                return render_template("search.html",f=fchk ,l=l)
            else:
                flash('No users found !!',category='danger')
    
    return render_template("search.html")

@app.route('/nfollow/<int:id>', methods=['GET','POST'])
@login_required
def nfollow(id):
    # if id != current_user.id:
    fc=Follow.query.filter_by(followed_id=id,follower_id=current_user.id).first()
    if fc:
        flash('You already follow this user!!',category='danger')
        return redirect("/search/username")
    else:
        f=Follow(followed_id=id,follower_id=current_user.id)
        db.session.add(f)
        db.session.commit()
        flash('followed!!',category='success')
        return redirect("/search/username")
    # return redirect(request.url)


@app.route('/nunfollow/<int:id>', methods=['GET','POST'])
@login_required
def nunfollow(id):
    # if id != current_user.id:
    f=Follow.query.filter_by(followed_id=id,follower_id=current_user.id).first()
    if f:
        Follow.query.filter_by(followed_id=id,follower_id=current_user.id).delete()
    # db.session.add(f)
        db.session.commit()
        flash('unfollowed!!',category='danger')
        return redirect("/search/username")
        # return redirect(request.url)

    else:
        flash("You are not following this user!! " ,category= 'danger')
        return redirect("/search/username")


@app.route('/ffollow/<int:id>', methods=['GET','POST'])
@login_required
def ffollow(id):
    # if id != current_user.id:
    fc=Follow.query.filter_by(followed_id=id,follower_id=current_user.id).first()
    if fc:
        flash('You already follow this user!!',category='danger')
        return redirect("/search/username")
    else:
        f=Follow(followed_id=id,follower_id=current_user.id)
        db.session.add(f)
        db.session.commit()
        flash('followed!!',category='success')
        return redirect("/search/username")
    # return redirect(request.url)


@app.route('/funfollow/<int:id>', methods=['GET','POST'])
@login_required
def funfollow(id):
    # if id != current_user.id:
    f=Follow.query.filter_by(followed_id=id,follower_id=current_user.id).first()
    if f:
        Follow.query.filter_by(followed_id=id,follower_id=current_user.id).delete()
    # db.session.add(f)
        db.session.commit()
        flash('unfollowed!!',category='danger')
        return redirect("/search/username")
        # return redirect(request.url)

    else:
        flash("You are not following this user!! " ,category= 'danger')
        return redirect("/search/username")



@app.route('/user/followers', methods=['GET','POST'])
@login_required
def followers():
    ck=Users.query.filter_by(id=current_user.id).first()
    chk=ck.followers.all()
    l=[]
    if chk:
        for i in chk:
            u=Users.query.filter_by(id=i.follower_id).first()
            l.append((i.follower_id,u.user_name))

    return render_template("followers.html",flwr=l)

@app.route('/user/following', methods=['GET','POST'])
@login_required
def following():
    ck=Users.query.filter_by(id=current_user.id).first()
    chk=ck.followed.all()
    l=[]
    if chk:
        for i in chk:
            u=Users.query.filter_by(id=i.followed_id).first()
            l.append((i.followed_id,u.user_name))
    return render_template("following.html",flwng=l)


@app.route('/flfollow/<int:id>', methods=['GET','POST'])
@login_required
def flfollow(id):
    # if id != current_user.id:
    fc=Follow.query.filter_by(followed_id=id,follower_id=current_user.id).first()
    if fc:
        # flash('You already follow this user!!',category='danger')
        return redirect("/profile/{cu}".format(cu=current_user.id))
    else:
        f=Follow(followed_id=id,follower_id=current_user.id)
        db.session.add(f)
        db.session.commit()
        # flash('followed!!',category='success')
        return redirect("/profile/{cu}".format(cu=current_user.id))


@app.route('/flunfollow/<int:id>', methods=['GET','POST'])
@login_required
def flunfollow(id):
    # if id != current_user.id:
    f=Follow.query.filter_by(followed_id=id,follower_id=current_user.id).first()
    if f:
        Follow.query.filter_by(followed_id=id,follower_id=current_user.id).delete()
    # db.session.add(f)
        db.session.commit()
        # flash('unfollowed!!',category='danger')
        return redirect("/profile/{cu}".format(cu=current_user.id))
        # return redirect(request.url)

    else:
        # flash("You are not following this user!! " ,category= 'danger')
        return redirect("/profile/{cu}".format(cu=current_user.id))



if __name__=="__main__":
    app.run(debug=True)