# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Teclib'ERP (<https://www.teclib-erp.com>).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from . import base


class OdooUsers(base.OdooModule):
    _name = "Users"
    _key = "users"

    def apply(self):
        super(OdooUsers, self).apply()

        users = self._datas.get(self._key, {}).get('users_data', {})
        for user in users:
            self.logger.info("User %s" % user)
            groups_id = []
            user_values = users[user]
            context = dict(user_values.get('context', {}))
            context.update(self._context)
            for group in user_values.get("groups_id", []):
                if group == "unlink all":
                    groups_id.append((5,))
                else:
                    groups_id.append(
                        (4, self._connection.get_ref(group)))

            login = user_values.get('login')
            if user_values.get('force_id', False):
                user_id = self.get_id_from_xml_id(user_values.get('force_id'))
            else:
                user_id = self.search('res.users', [('login', '=', login)], order='id', context=context)

            vals = {}
            if login:
                vals['login'] = login
            if groups_id:
                vals['groups_id'] = groups_id
            context['active_test'] = False
            if not user_id:
                self.execute_odoo('res.users', 'create', [vals], {'context': context})
            else:
                self.execute_odoo('res.users', 'write', [user_id, vals], {'context': context})
