from django.conf import settings
from django.contrib.auth.models import AbstractUser as DjangoUser
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from launchbox.core.models import (
    SoftDeletableMixin,
    TimeStampedMixin,
    UUIDPrimaryKeyMixin,
)

from .application import Application
from .content import Content


class Page(UUIDPrimaryKeyMixin, TimeStampedMixin, models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='pages',
        verbose_name=_('application'),
    )
    title = models.CharField(_('page title'), max_length=64)
    description = models.TextField(
        _('description'),
        blank=True,
        null=True,
        default=None,
    )
    slug = models.SlugField(_('page slug'), max_length=64, db_index=True)
    is_inherited = models.BooleanField(_('inherited from parent'), default=True)
    published_at = models.DateTimeField(
        _('publish date and time'),
        null=True,
        blank=True,
        default=None,
    )
    closed_at = models.DateTimeField(
        _('close date and time'),
        null=True,
        blank=True,
        default=None,
    )
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('user who publish'),
        blank=True,
        null=True,
        default=None,
        editable=False,
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('user who close'),
        blank=True,
        null=True,
        default=None,
        editable=False,
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='child_pages',
        verbose_name=_('parent page'),
        blank=True,
        null=True,
        default=None,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('owner'),
    )
    contents = models.ManyToManyField(
        Content,
        related_name='pages',
        through='content.PageContentRelation',
        verbose_name=_('contents'),
        blank=True,
    )

    class Meta:
        db_table = 'launchbox_page'
        verbose_name = _('page')
        verbose_name_plural = _('pages')
        ordering = ('-created_at',)
        constraints = [
            # If published_at is None, closed_at should be None
            models.CheckConstraint(
                check=(
                    models.Q(published_at__isnull=False)
                    | models.Q(closed_at__isnull=True)
                ),
                name='published_at_is_none_then_closed_at_is_none',
            ),
            # published_at should be before closed_at
            models.CheckConstraint(
                check=(
                    models.Q(published_at__lt=models.F('closed_at'))
                    | models.Q(published_at__isnull=True)
                    | models.Q(closed_at__isnull=True)
                ),
                name='published_at_is_before_closed_at',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.application} / {self.title}'

    @property
    def child_page_count(self):
        return self.child_pages.all().count()

    @property
    def is_private(self):
        return self.published_at is None or self.published_at > now()

    @property
    def is_closed(self):
        return self.closed_at is not None and self.closed_at <= now()

    @property
    def is_public(self):
        return not self.is_private and not self.is_closed

    @property
    def show_count(self) -> int:
        return self.pageshow_set.all().count()

    @property
    def view_count(self) -> int:
        return self.pageview_set.all().count()

    @property
    def view_sum(self) -> int:
        return (
            self.pageview_set.all()
            .aggregate(view_sum=models.Sum('value'))
            .get('view_sum', 0)
        )

    @property
    def like_count(self):
        return self.pagelike_set.all().filter(deleted_at__isnull=True).count()

    @property
    def like_sum(self):
        return (
            self.pagelike_set.all()
            .filter(deleted_at__isnull=True)
            .aggregate(like_sum=models.Sum('value'))
            .get('like_sum', 0)
        )

    @property
    def follow_count(self):
        return self.pagefollow_set.all().filter(deleted_at__isnull=True).count()

    def show(
        self,
        *,
        user: DjangoUser | None = None,
        user_identifier: str | None = None,
    ) -> 'PageShow':
        return PageShow.objects.create(
            page=self,
            user=user,
            user_identifier=user_identifier,
        )

    def view(
        self,
        *,
        user: DjangoUser | None = None,
        user_identifier: str | None = None,
        value: int | None = None,
    ) -> 'PageView':
        return PageView.objects.create(
            page=self,
            user=user,
            user_identifier=user_identifier,
            value=value,
        )

    def remove_from_view_history(self, *, user: DjangoUser) -> int:
        return (
            self.pageview_set.all()
            .filter(deleted_at__isnull=True, user=user)
            .update(deleted_at=now())
        )

    def like(
        self,
        *,
        user: DjangoUser,
        value: int | None = None,
    ) -> 'PageLike':
        like, is_created = PageLike.objects.get_or_create(
            page=self,
            user=user,
            value=value,
        )
        if not is_created and like.is_deleted:
            like.revive()
        return like

    def unlike(self, *, user: DjangoUser, value: int | None = None) -> 'PageLike':
        try:
            like = self.pagelike_set.all().get(deleted_at__isnull=True, user=user)
        except PageLike.DoesNotExist:
            if like.value != value:
                like.value = value
                like.save()
            return like
        else:
            if like.value != value:
                like.value = value
            like.soft_delete()
            return like

    def is_liked(self, *, user: DjangoUser) -> bool:
        return self.pagelike_set.all().exists(deleted_at__isnull=True, user=user)

    def like_value(self, *, user: DjangoUser) -> int:
        try:
            like = self.pagelike_set.all().get(deleted_at__isnull=True, user=user)
            return like.value or 0
        except PageLike.DoesNotExist:
            return 0

    def follow(self, *, user: DjangoUser) -> 'PageFollow':
        follow, is_created = PageFollow.objects.get_or_create(page=self, user=user)
        if not is_created and follow.is_deleted:
            follow.revive()
        return follow

    def unfollow(self, *, user: DjangoUser) -> 'PageFollow':
        try:
            follow = self.pagefollow_set.all().get(deleted_at__isnull=True, user=user)
        except PageFollow.DoesNotExist:
            return follow
        else:
            follow.soft_delete()
            return follow

    def is_following(self, *, user: DjangoUser) -> bool:
        return self.pagefollow_set.all().exists(deleted_at__isnull=True, user=user)


class PageContentRelation(
    UUIDPrimaryKeyMixin,
    TimeStampedMixin,
    models.Model,
):
    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name=_('content'),
    )
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name=_('page'),
    )

    class Meta:
        db_table = 'launchbox_page_content'
        verbose_name = _('page content relation')
        verbose_name_plural = _('page content relations')
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['page', 'content'],
                name='unique_content_per_page',
            ),
        ]


class PageLabelType(
    SoftDeletableMixin,
    UUIDPrimaryKeyMixin,
    TimeStampedMixin,
    models.Model,
):
    name = models.CharField(_('type name'), max_length=32)
    slug = models.SlugField(_('type slug'), max_length=32, unique=True)
    max_per_page = models.PositiveIntegerField(
        _('the numbers of max labelings per page'),
        null=True,
        blank=True,
        default=None,
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.PROTECT,
        verbose_name=_('application'),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('owner'),
    )

    class Meta:
        db_table = 'launchbox_page_label_type'
        verbose_name = _('page label type')
        verbose_name_plural = _('page label types')
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.name


class PageLabel(
    SoftDeletableMixin,
    UUIDPrimaryKeyMixin,
    TimeStampedMixin,
    models.Model,
):
    name = models.CharField(_('label name'), max_length=32)
    type = models.ForeignKey(
        PageLabelType,
        on_delete=models.CASCADE,
        verbose_name=_('label type'),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('owner'),
    )

    class Meta:
        db_table = 'launchbox_page_label'
        verbose_name = _('page label')
        verbose_name_plural = _('page labels')
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['type', 'name'],
                name='unique_name_per_type',
            ),
        ]

    def __str__(self) -> str:
        return self.name


class PageLabeling(
    UUIDPrimaryKeyMixin,
    TimeStampedMixin,
    models.Model,
):
    label = models.ForeignKey(
        PageLabel,
        on_delete=models.CASCADE,
        verbose_name=_('label'),
    )
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        verbose_name=_('page'),
    )

    class Meta:
        db_table = 'launchbox_page_labeling'
        verbose_name = _('page labeling')
        verbose_name_plural = _('page labelings')
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['page', 'label'],
                name='unique_label_per_page',
            ),
        ]


class PageMetaItem(
    UUIDPrimaryKeyMixin,
    TimeStampedMixin,
    models.Model,
):
    name = models.CharField(_('meta name'), max_length=32)
    value_html = models.TextField(_('meta html'), blank=True, null=True, default=None)
    value_json = models.JSONField(_('meta json'), blank=True, null=True, default=None)
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='meta_items',
        verbose_name=_('page'),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name=_('owner'),
    )

    class Meta:
        db_table = 'launchbox_page_meta_item'
        verbose_name = _('page meta item')
        verbose_name_plural = _('page meta items')
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.name


class PageAndUserRelationMixin(UUIDPrimaryKeyMixin, TimeStampedMixin, models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_('user'),
        null=True,
        blank=True,
        default=None,
    )
    user_identifier = models.CharField(
        _('user identifier'),
        max_length=256,
        null=True,
        blank=True,
        default=None,
    )
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        verbose_name=_('page'),
    )

    class Meta:
        abstract = True
        constraints = [
            # require user or user identifier
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False)
                    | models.Q(user_identifier__isnull=False)
                ),
                name='require_user_or_user_identifier',
            ),
        ]

    def __str__(self) -> str:
        identifier = self.user or self.user_identifier
        return f'{self.page} / {identifier} / {self.created_at}'


class PageAndUserNestableRelationMixin(PageAndUserRelationMixin):
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name=_('parent'),
        blank=True,
        null=True,
        default=None,
    )

    class Meta:
        abstract = True


class PageAndUserUniqueRelationMixin(PageAndUserRelationMixin):
    class Meta(PageAndUserRelationMixin.Meta):
        abstract = True
        constraints = [
            *PageAndUserRelationMixin.Meta.constraints,
            models.UniqueConstraint(
                fields=['page', 'user'],
                name='unique_user_per_page',
            ),
        ]


class PageShow(PageAndUserRelationMixin):
    class Meta:
        db_table = 'launchbox_page_show'
        verbose_name = _('page show')
        verbose_name_plural = _('page shows')
        ordering = ('-created_at',)


class PageView(SoftDeletableMixin, PageAndUserRelationMixin):
    value = models.IntegerField(_('value'), null=True, blank=True, default=None)

    class Meta:
        db_table = 'launchbox_page_view'
        verbose_name = _('page view')
        verbose_name_plural = _('page views')
        ordering = ('-created_at',)


class PageLike(SoftDeletableMixin, PageAndUserUniqueRelationMixin):
    value = models.IntegerField(_('value'), null=True, blank=True, default=None)

    class Meta:
        db_table = 'launchbox_page_like'
        verbose_name = _('page like')
        verbose_name_plural = _('page likes')
        ordering = ('-created_at',)


class PageFollow(SoftDeletableMixin, PageAndUserUniqueRelationMixin):
    class Meta:
        db_table = 'launchbox_page_follow'
        verbose_name = _('page follow')
        verbose_name_plural = _('page follows')
        ordering = ('-created_at',)


class PageReaction(PageAndUserNestableRelationMixin):
    type = models.SlugField(_('reaction type'))
    message = models.TextField(
        _('reaction message'),
        null=True,
        blank=True,
        default=None,
    )
    value = models.IntegerField(
        _('reaction value'),
        null=True,
        blank=True,
        default=None,
    )
    meta = models.JSONField(_('reaction meta'), null=True, blank=True, default=None)

    class Meta:
        db_table = 'launchbox_page_reaction'
        verbose_name = _('page reaction')
        verbose_name_plural = _('page reactions')
        ordering = ('-created_at',)
