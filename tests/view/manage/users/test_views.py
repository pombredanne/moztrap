# coding: utf-8
"""
Tests for user management views.

"""
from django.core.urlresolvers import reverse

from tests import case



class UsersTest(case.view.manage.ListViewTestCase,
                case.view.NoCacheTest,
                ):
    """Test for users manage list view."""
    form_id = "manage-users-form"
    perm = "manage_users"
    name_attr = "username"


    def setUp(self):
        """Any access to this view requires manage_users perm."""
        super(UsersTest, self).setUp()
        self.add_perm(self.perm)


    @property
    def factory(self):
        """The model factory for this manage list."""
        return self.F.UserFactory


    @property
    def url(self):
        """Shortcut for manage-users url."""
        return reverse("manage_users")


    def test_create_link_requires_perms(self):
        """This test from superclass doesn't apply here."""
        pass


    def test_delete_requires_permission(self):
        """This test from superclass doesn't apply here."""
        pass


    def test_activate(self):
        """Can activate objects in list."""
        s = self.factory.create(is_active=False, username="foo")

        self.get_form(params={"filter-username": "foo"}).submit(
            name="action-activate",
            index=0,
            headers={"X-Requested-With": "XMLHttpRequest"},
            )

        self.assertTrue(self.refresh(s).is_active)


    def test_deactivate(self):
        """Can deactivate objects in list."""
        s = self.factory.create(is_active=True, username="foo")

        self.get_form(params={"filter-username": "foo"}).submit(
            name="action-deactivate",
            index=0,
            headers={"X-Requested-With": "XMLHttpRequest"},
            )

        self.assertFalse(self.refresh(s).is_active)


    def test_delete(self):
        """Can delete objects from list."""
        o = self.factory.create(username="foo")

        self.get_form(params={"filter-username": "foo"}).submit(
            name="action-delete",
            index=0,
            headers={"X-Requested-With": "XMLHttpRequest"}
            )

        with self.assertRaises(self.model.User.DoesNotExist):
            self.refresh(o)


    def test_filter_by_username(self):
        """Can filter by username."""
        self.factory.create(username="User 1")
        self.factory.create(username="User 2")

        res = self.get(params={"filter-username": "1"})

        self.assertInList(res, "User 1")
        self.assertNotInList(res, "User 2")


    def test_filter_by_email(self):
        """Can filter by email."""
        self.factory.create(username="User 1", email="one@example.com")
        self.factory.create(username="User 2", email="two@example.com")

        res = self.get(params={"filter-email": "one"})

        self.assertInList(res, "User 1")
        self.assertNotInList(res, "User 2")


    def test_filter_by_active(self):
        """Can filter by is_active."""
        self.factory.create(username="User 1", is_active=True)
        self.factory.create(username="User 2", is_active=False)

        res = self.get(params={"filter-active": "1"})

        self.assertInList(res, "User 1")
        self.assertNotInList(res, "User 2")


    def test_filter_by_not_active(self):
        """Can filter by not is_active."""
        self.factory.create(username="User 1", is_active=True)
        self.factory.create(username="User 2", is_active=False)

        res = self.get(params={"filter-active": "0"})

        self.assertInList(res, "User 2")
        self.assertNotInList(res, "User 1")


    def test_filter_by_role(self):
        """Can filter by role."""
        r = self.F.RoleFactory.create()
        u = self.factory.create(username="User 1")
        u.groups.add(r)
        self.factory.create(username="User 2")

        res = self.get(params={"filter-role": str(r.id)})

        self.assertInList(res, "User 1")
        self.assertNotInList(res, "User 2")


    def test_sort_by_username(self):
        """Can sort by username."""
        self.factory.create(username="User 1")
        self.factory.create(username="User 2")

        res = self.get(params={"sortfield": "username", "sortdirection": "desc"})

        self.assertOrderInList(res, "User 2", "User 1")


    def test_sort_by_email(self):
        """Can sort by email."""
        self.factory.create(username="User 1", email="one@example.com")
        self.factory.create(username="User 2", email="two@example.com")

        res = self.get(params={"sortfield": "email", "sortdirection": "desc"})

        self.assertOrderInList(res, "User 2", "User 1")



class AddUserTest(case.view.FormViewTestCase,
                  case.view.NoCacheTest,
                  ):
    """Tests for add user view."""
    form_id = "user-add-form"


    @property
    def url(self):
        """Shortcut for add-user url."""
        return reverse("manage_user_add")


    def setUp(self):
        """Add manage-users permission to user."""
        super(AddUserTest, self).setUp()
        self.add_perm("manage_users")


    def test_success(self):
        """Can add a user with basic data, including a version."""
        g = self.F.RoleFactory.create()
        form = self.get_form()
        form["username"] = "someone ùê"
        form["email"] = "someone@example.com"
        form["is_active"] = "1"
        form["groups"] = [str(g.id)]

        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_users"))

        res.follow().mustcontain("User 'someone ùê' added.")

        u = self.model.User.objects.get(username="someone ùê")
        self.assertEqual(u.email, "someone@example.com")
        self.assertTrue(u.is_active)
        self.assertEqual(u.groups.get(), g)


    def test_error(self):
        """Bound form with errors is re-displayed."""
        res = self.get_form().submit()

        self.assertEqual(res.status_int, 200)
        res.mustcontain("This field is required.")


    def test_requires_manage_users_permission(self):
        """Requires manage-users permission."""
        res = self.app.get(
            self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")



class EditUserTest(case.view.FormViewTestCase,
                   case.view.NoCacheTest,
                   ):
    """Tests for edit-user view."""
    form_id = "user-edit-form"


    def setUp(self):
        """Setup for user edit tests; create a user, add perm."""
        super(EditUserTest, self).setUp()
        self.user = self.F.UserFactory.create()
        self.add_perm("manage_users")


    @property
    def url(self):
        """Shortcut for edit-user url."""
        return reverse(
            "manage_user_edit", kwargs=dict(user_id=self.user.id))


    def test_requires_manage_users_permission(self):
        """Requires manage-users permission."""
        res = self.app.get(self.url, user=self.F.UserFactory.create(), status=302)

        self.assertRedirects(res, "/")


    def test_save_basic(self):
        """Can save updates; redirects to manage users list."""
        form = self.get_form()
        form["username"] = "new name ùê"
        res = form.submit(status=302)

        self.assertRedirects(res, reverse("manage_users"))

        res.follow().mustcontain("Saved 'new name ùê'.")

        p = self.refresh(self.user)
        self.assertEqual(unicode(p.username), u"new name ùê")


    def test_errors(self):
        """Test bound form redisplay with errors."""
        form = self.get_form()
        form["username"] = ""
        res = form.submit(status=200)

        res.mustcontain("This field is required.")
