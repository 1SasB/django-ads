from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings
from django.core.files.storage import FileSystemStorage
fs = FileSystemStorage(location='/photos')
class Ad(models.Model) :
    title = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
    )
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    text = models.TextField()
    picture = models.ImageField(upload_to='photos',blank=True,null=True)
    pic_content_type = models.CharField(max_length=265,null=True,help_text='The MIMEType of the file')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL,through='Fav',related_name='favourite_ads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(validators=[MinLengthValidator(3,'comment must be greater than 3 characters')])
    ad =  models.ForeignKey(Ad,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    # def __str__(self):
    #     return self.text
    def __str__(self):
        if len(self.text) < 15 : 
            return self.text
        
        return str(self.text[:11])+'...'


class Fav(models.Model):
    ad = models.ForeignKey(Ad,on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('ad','user')

    def __str__(self):
        return '%s likes %s'%(self.user.username,self.ad.title)