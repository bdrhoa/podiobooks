"""Podiobooks Main Models File"""

from __future__ import division
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.template.loader import render_to_string

# pylint: disable=C0111,R0201,W0232

class Award(models.Model):
    """Awards are just that: awards for a title, like winning a Parsec, etc."""
    slug = models.SlugField()
    name = models.CharField(blank=True, max_length=255)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to='images/awards', max_length=255)
    # Note - titles are available as title_set.all()
    deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'award_detail', [self.slug]


class Category(models.Model):
    """Categories describe titles for easy of browsing and for recommendations."""
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=50)
    # Note - titles are available as title_set.all()
    # Note - for SQL purposes, titles are 'title'
    deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'category_detail', [self.slug]


class Contributor(models.Model):
    """A contributor is one who had done work on a title. For a book, it's an
    author or authors."""
    slug = models.SlugField(max_length=1000) # For multi-contributor books, can get long
    user = models.ForeignKey(User, null=True, blank=True, related_name='contributor_info') #User is an OOTB Django Auth Model
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)
    # Note: Titles are available a title_set.all()
    # Note: TitleContributor Objects (intermediate table) are available as titlecontributors.all()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __unicode__(self):
        return self.display_name

    @models.permalink
    def get_absolute_url(self):
        return 'contributor_detail', [self.slug]


class ContributorType(models.Model):
    """Types of contributors: author, key grid, best boy, director, etc."""
    slug = models.SlugField()
    name = models.CharField(max_length=255)
    byline_text = models.CharField(max_length=255)
    # Note: TitleContributor Objects (intermediate table) are available as titlecontributors.all()

    class Meta:
        verbose_name_plural = "Contributor Types"

    def __unicode__(self):
        return self.name


class Episode(models.Model):
    """Titles are composed of Episodes. For a book, these are chapters or
    divisions of the book into smaller parts. For a comic book, it would be each
    issue of the comic."""
    title = models.ForeignKey('Title', related_name='episodes')
    name = models.CharField(max_length=255)
    sequence = models.IntegerField() #Order in the Story
    description = models.TextField(blank=True)
    url = models.URLField()
    filesize = models.IntegerField(default=0, help_text="In bytes, corresponds to 'length' in RSS feed") #Size of the media file
    duration = models.CharField(max_length=20, default='45:00', help_text='Duration of the media file in minutes:seconds') #Length of the media file (in minutes)
    contributors = models.ManyToManyField('Contributor', through='EpisodeContributor')
    deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title__name', 'sequence']

    def __unicode__(self):
        return self.title.name + ': Episode #' + str(self.sequence) + ': ' + self.name

    @models.permalink
    def get_absolute_url(self):
        return ('episode_detail', [self.id]) # pylint: disable=E1101

    def _get_filesize_mb(self):
        return round(self.filesize / 1024.0 / 1024.0, 2)

    filesize_mb = property(_get_filesize_mb)


class EpisodeContributor(models.Model):
    """Join table to associate contributors to titles."""
    episode = models.ForeignKey('Episode', related_name='episodecontributors')
    contributor = models.ForeignKey('Contributor', related_name='episodecontributors')
    contributor_type = models.ForeignKey('ContributorType', related_name='episodecontributors')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Episode Contributors"


class License(models.Model):
    """A collection of defined licenses for works. Creative Commons, All Rights
    Reserved, etc."""
    slug = models.SlugField()
    text = models.CharField(max_length=255)
    url = models.URLField()
    image_url = models.URLField()
    code = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['slug']

    def __unicode__(self):
        return self.slug


MEDIA_NAME_CHOICES = (
    ('Print Version', 'Print Version'),
    ('Kindle Version', 'Kindle Version'),
    ('Smashwords Version', 'Smashwords Version'),
    )


class Media(models.Model):
    """Media are links to other forms of the title. In the case of books, these
    would be dead tree editions, epub, etc."""
    title = models.ForeignKey('Title', related_name='media')
    name = models.CharField(max_length=255, default='Print Version', choices=MEDIA_NAME_CHOICES)
    identifier = models.CharField(max_length=255, blank=True, help_text="ISBN or Product ID")
    url = models.CharField(max_length=255, blank=True)
    deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "media"
        ordering = ['name']

    def __unicode__(self):
        return self.name

class Rating(models.Model):
    """The last rating that was loaded from the pb1 site"""
    last_rating_id = models.IntegerField(default=0, db_index=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'date_created'

    def __unicode__(self):
        return str(self.last_rating_id)


class Series(models.Model):
    """Titles can belong to a series, which allows for higher level grouping."""
    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "series"
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'series_detail', [self.slug]


class Title(models.Model):
    """Title is the central class, and represents the media item as a whole.
    Example: A book. A season of a TV Series. A volume of a Comic Book. A set of
    college lectures."""

    name = models.CharField(max_length=255)
    series = models.ForeignKey('Series', null=True, blank=True, related_name='titles')
    series_sequence = models.IntegerField(default=1, verbose_name='Series Sequence')
    description = models.TextField()
    slug = models.SlugField(max_length=255, unique=True)
    cover = models.ImageField(upload_to='images/covers', blank=True, null=True)
    license = models.ForeignKey('License', null=True, related_name='titles')
    display_on_homepage = models.BooleanField(default=False, db_index=True, verbose_name='Disp. On Homepage')
    is_adult = models.BooleanField(default=False, db_index=True, verbose_name='Is Adult')
    is_explicit = models.BooleanField(default=False, db_index=True, verbose_name='Is Explicit')
    is_family_friendly = models.BooleanField(default=False, db_index=True, verbose_name='Is Family Friendly')
    is_for_kids = models.BooleanField(default=False, db_index=True, verbose_name='Is For Kids')
    promoter_count = models.IntegerField(default=0, db_index=True)
    detractor_count = models.IntegerField(default=0, db_index=True)
    deleted = models.BooleanField(default=False, verbose_name='Deleted?')
    contributors = models.ManyToManyField('Contributor', through='TitleContributor') #related_name doesn't work with manual intermediary tables
    # Note: TitleContributor Objects (intermediate table) are available as titlecontributors.all()
    byline = models.CharField(max_length=1024, blank=True) # This is a formatted cache of the title contributors
    categories = models.ManyToManyField('Category', through='TitleCategory') #related_name doesn't work with manual intermediary tables
    # Note: TitleCategory Objects (intermediate table) are available as titlecategories.all()
    category_list = models.CharField(max_length=1024, blank=True) # This is a formatted cache of the categories
    awards = models.ManyToManyField('Award', null=True, blank=True, related_name='titles')
    libsyn_show_id = models.CharField(max_length=50, db_index=True, blank=True, verbose_name='LibSyn Show ID', help_text='Starts with k-')
    itunes_adam_id = models.IntegerField(null=True, blank=True, verbose_name='iTunes ADAM Id', help_text='From iTunes Page URL for Podcast')
    podiobooker_blog_url = models.URLField(max_length=255, null=True, blank=True,verbose_name='Blog URL', help_text='Full URL to Blog Post Announcing Book')
    # Note: episodes are available as episodes.all()
    # Note: media are available as media.all()
    # Note: promos are available as promos.all()
    date_created = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Date Created')
    date_updated = models.DateTimeField(auto_now=True, db_index=True, verbose_name='Date Updated')

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.slug

    @models.permalink
    def get_absolute_url(self):
        return ('title_detail', [self.slug])

    def net_promoter_score(self):
        total_count = self.promoter_count + self.detractor_count
        if total_count:
            return int((self.promoter_count / total_count) * 100)
        else:
            return 0

    def description_br(self):
        return self.description.replace('\n', '\n<br/>') # pylint: disable=E1101

    def computed_rating(self):
        nps = self.net_promoter_score() / 100
        return nps * 5
    
    def get_byline(self):
        """ return a text-only byline (i.e. no HTML) """
        ret = ""
        for (i, title_contributor) in enumerate(self.titlecontributors.all()):
            if title_contributor.contributor_type.slug == "author":
                if i == 0:
                    ret += "by "
                else:
                    ret += "and "
            else:
                ret += title_contributor.contributor_type.byline_text + " "
            
            ret += title_contributor.contributor.__unicode__()
            ret += " "
        ret = ret.replace("  ", " ")        
        return ret
            

class TitleCategory(models.Model):
    """
        Join table to associate categories to titles.
        This is built as a non-automatic model in order to get the signal hooks to work
    """
    title = models.ForeignKey('Title', related_name='titlecategories')
    category = models.ForeignKey('Category', related_name='titlecategories')

    class Meta:
        verbose_name_plural = "Title Categories"


# pylint: disable=W0613
def update_category_list(sender, instance, **kwargs):
    """ Update category list cache on titles when a new title category is added...hooked to pre_save trigger for titlecategory below """
    categories = instance.title.categories.all()
    category_list = render_to_string('core/title/title_category_list.html', {'categories': categories, })

    instance.title.category_list = category_list
    instance.title.save()

post_save.connect(update_category_list, sender=TitleCategory)


class TitleContributor(models.Model):
    """Join table to associate contributors to titles."""
    title = models.ForeignKey('Title', related_name='titlecontributors')
    contributor = models.ForeignKey('Contributor', related_name='titlecontributors')
    contributor_type = models.ForeignKey('ContributorType', related_name='titlecontributors')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Title Contributors"
        ordering = ['contributor_type__slug', 'date_created']

    def __unicode__(self):
        return self.contributor.display_name + ": " + self.contributor_type.name + " of " + self.title.name


class TitleUrl(models.Model):
    """Allows us to have several links for a book, for display. For utility."""
    title = models.ForeignKey('Title', related_name='urls')
    url = models.URLField()
    linktext = models.CharField(max_length=255)
    displayorder = models.IntegerField(null=False, default=1)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "TitleUrls"

