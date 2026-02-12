import sqlalchemy as sa
import sqlalchemy.orm as so
from microblog import app,db
from microblog.models import User,Post,Message,Notification

@app.shell_context_processor
def make_shell_context():
  return {'sa':sa, 'so':so,'db':db, 'User':User, 'Post':Post, 'Message':Message, 'Notification':Notification}

if __name__ == '__main__':
  app.run(debug=True)