# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Teclib'ERP (<https://www.teclib-erp.com>).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from . import base


class OdooUsers(base.OdooModule):
    _name = "Users"
    _key = "users"

    def apply(self):
        super(OdooUsers, self).apply()

        users = self._datas.get(self._key, {}).get('users', {})
        for user in users:
            groups_id = []
            for group in users[user].get("groups_id", []):
                if group == "unlink all":
                    groups_id.append((5,))
                else:
                    groups_id.append(
                        (4, self._connection.get_ref(group)))

            login = users[user].get('login')
            if users[user].get('force_id', False):
                user_id = self.get_id_from_xml_id(users[user].get('force_id'))
            else:
                user_id = self.search('res.users', [('login', '=', login)], order='id', context=self._context)

            vals = {}
            if login:
                vals['login'] = login
            if groups_id:
                vals['groups_id'] = groups_id
            self._context['active_test'] = False
            if not user_id:
                self.execute_odoo('res.users', 'create', [vals], {'context': self._context})
            else:
                self.execute_odoo('res.users', 'write', [user_id, vals], {'context': self._context})
