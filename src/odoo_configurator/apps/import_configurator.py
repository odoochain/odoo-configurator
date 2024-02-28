# -*- coding: utf-8 -*-
# Copyright (C) 2023 - Teclib'ERP (<https://www.teclib-erp.com>).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import base64
from collections import OrderedDict
import os
from . import base

EXCLUDE_FIELDS = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'parent_path']


def compare_field(field):
    if field == 'name':
        res = 0
    elif field.endswith('_id'):
        res = 10
    elif field.endswith('_ids'):
        res = 20
    else:
        res = 99
    return res


def get_fle_type_from_binary(binary):
    if binary.startswith(b'\x89PNG\r\n\x1a\n\x00'):
        return 'png'
    if binary.startswith(b'\xff\xd8\xff'):
        return 'jpg'
    if binary.startswith(b'\x00\x00\x01\x00'):
        return 'ico'
    return 'bin'


def compare_xmlid(xmlid):
    module = xmlid.split('.')[0]
    if module == 'base':
        res = 'A'
    elif module.startswith('teclib') or module.startswith('hodei'):
        res = 'T'
    elif module.startswith('__'):
        res = 'Z'
    else:
        res = 'F'
    return res


def sort_fields(field_names):
    field_names = sorted(field_names, key=compare_field)
    return field_names


class ImportConfigurator(base.OdooModule):
    _name = "Import Configurator"

    rec_to_xmlid_cache = {}
    model_fields = {}
    display_name_prefix_fields = []

    def get_configurator_records(self, model, domain=[], excluded_fields=[], force_export_fields=[],
                                 order_by='', display_name_prefix_fields='', group_by=[], with_load=False):
        files = []
        self.display_name_prefix_fields = display_name_prefix_fields
        if not model:
            return ''
        records = self.search(model, domain, order=order_by)
        if not records:
            return ''

        res = ''
        prev_record_group = ''
        model_id = self.search('ir.model', [('model', '=', model)])[0]
        self.load_model_fields(model)
        for i, record in enumerate(records):
            self.logger.info("Export %s : %s/%s", model, i, len(records))
            record_group = model_id['name'].title().replace(':', '')
            if group_by:
                if isinstance(record[group_by], list):
                    group_by_name = record[group_by][1]
                else:
                    group_by_name = record[group_by]
                record_group = '%s - %s' % (group_by_name, record_group)
            if prev_record_group != record_group:
                res += '\n%s:' % record_group
                if with_load:
                    res += '\n%s%s: %s' % (" " * 4, 'load', with_load)
                    res += '\n%s%s: %s' % (" " * 4, 'model', model)
                res += '\n%s%s:' % (" " * 4, 'datas')
                prev_record_group = record_group

            values = ""
            rec_name = self.get_record_name(record, model)
            prefix = self.get_record_prefix(record)
            if prefix:
                rec_name = '%s %s' % (prefix, rec_name)

            xmlid = self.get_xmlid(model, record.get('id'))
            if not xmlid:
                xmlid = self.compute_xml_id(record)
            res += '\n%s%s:' % (" " * 4 * 2, rec_name)
            res += '\n%s%s: %s' % (" " * 4 * 3, 'model', model)
            res += '\n%s%s: %s' % (" " * 4 * 3, 'force_id', xmlid)
            res += '\n%s%s:' % (" " * 4 * 3, 'values')

            field_names = sort_fields(self.model_fields.keys())
            for key in field_names:
                field = self.model_fields[key]['field']

                if not self.field_is_exclude(field, excluded_fields):
                    try:
                        default = self.model_fields[key]['default']
                        if (default != record[key] and record[key]) or key in force_export_fields:
                            field_value, files = self.get_field_value(record, field, files)
                            values += field_value
                    except Exception as e:
                        self.logger.error(e, exc_info=True)

            res += values
            res += '\n'

        return res, files

    def load_model_fields(self, model):
        self.model_fields = dict()
        fields = self.search('ir.model.fields', [('model', '=', model)])
        for field in fields:
            self.model_fields[field['name']] = {'field': field,
                                                'default': self.default_get(model, field['name'])}

    def field_is_exclude(self, field, excluded_fields=[]):
        field_name = field.get('name')
        if field_name in EXCLUDE_FIELDS:
            return True
        if field_name in excluded_fields:
            return True
        if field_name.startswith('__'):
            return True
        if not field.get('store', True):
            return True
        if field.get('related', False):
            return True

    def get_field_value(self, record, field, files):
        field_name = field.get('name')
        model = field.get('model')
        field_type = field.get('ttype')
        if field_type in ['one2many']:
            name = ''
        elif field_type in ['binary']:
            if field_name in ['image_1024', 'image_128', 'image_256', 'image_512']:
                name = ''
            binary_data = base64.b64decode(record[field_name])
            file_name = '%s_%s' % (model.replace('.', '_'), record.id)
            if model == 'ir.attachment' and '.' in record.name:
                ext = record.name.split('.')[-1]
            else:
                ext = get_fle_type_from_binary(binary_data)
            file_name = '%s.%s' % (file_name, ext)
            files.append((file_name, binary_data))
            name = "\n%s%s: %s" % (" " * 4 * 4, field_name, 'get_image_local("%s")' % file_name)
        elif field_type == 'many2many':
            # Todo : import many2many values
            # rec_values = ''
            # xmlid_list = sort_xml_ids([val.get_xml_id()[val.id] for val in record[field_name]])
            # for xmlid in xmlid_list:
            #     if xmlid:
            #         rec_values += '\n%s- %s' % (" " * (2 + 4 * 4), xmlid)
            # if rec_values:
            #     name = '\n%s%s/id: %s' % (" " * 4 * 4, field_name, rec_values)
            name = ''

        elif field_type in ['many2one']:
            if record[field_name]:
                xmlid = self.get_xmlid(field['relation'], record[field_name][0])
                if xmlid:
                    name = "\n%s%s/id: %s" % (" " * 4 * 4, field_name, xmlid)
            else:
                name = "\n%s%s.id: %s" % (" " * 4 * 4, field_name, 'False')
        elif field_type in ['char', 'date', 'datetime', 'selection']:
            val_str = record[field_name] and str(record[field_name]) or ''
            if '{{' in val_str:
                val_str = val_str.replace('{{', '\\{\\{')
                multiline_text = (" " * 4 * 5) + val_str.replace('\n', '\n%s' % (" " * 4 * 5))
                name = '\n%s%s: |\n%s' % (" " * 4 * 4, field_name, multiline_text)
            else:
                name = '\n%s%s: "%s"' % (" " * 4 * 4, field_name, val_str.replace('"', '\\"'))

        elif field_type in ['html', 'text']:
            multiline_text = (" " * 4 * 5) + record[field_name].replace('\n', '\n%s' % (" " * 4 * 5))
            name = '\n%s%s: |\n%s' % (" " * 4 * 4, field_name, multiline_text)
        else:
            name = "\n%s%s: %s" % (" " * 4 * 4, field_name, record[field_name])

        return name, files

    def get_record_name(self, record, model):
        try:
            if 'name' in record:
                if record.get('name'):
                    return record.get('name').title().replace(':', '')
                else:
                    return ''
            elif 'display_name' in record:
                return record.get('display_name').replace(':', '')
            elif 'key' in record:
                return record.get('key')
            elif 'ref' in record:
                return record.get('ref')
            else:
                return model + '_' + record.get('id')
        except Exception as e:
            self.logger.error(e, exc_info=True)
            pass
        return ''

    def get_record_prefix(self, record):
        prefix_words = []
        for field_name in self.display_name_prefix_fields:
            field_id = self.model_fields[field_name]['field']
            if field_id['ttype'] == 'many2one' and record[field_name]:
                related_record = self.search(field_id['relation'], [('id', '=', record[field_name][0])])
                prefix = related_record and related_record[0]['name']
            else:
                prefix = record[field_name]
            if prefix:
                prefix_words.append(prefix)
        return ' '.join(prefix_words)

    def get_xmlid(self, model, res_id):
        if (model, res_id) in self.rec_to_xmlid_cache:
            return self.rec_to_xmlid_cache[(model, res_id)]
        xmlid = self.get_xml_id_from_id(model, res_id)
        self.rec_to_xmlid_cache[(model, res_id)] = xmlid
        return xmlid

    def compute_xml_id(self, record, retry=0):
        xml_id = 'external_config.%s_%s' % (record['model'].replace('.', '_'), str(record['id']+retry).zfill(5))
        if not self._connection.get_id_from_xml_id(xml_id, no_raise=True):
            return xml_id
        else:
            retry += 1
            return self.compute_xml_id(record, retry)

    def apply(self):
        super(ImportConfigurator, self).apply()
        for key in self._datas:
            if isinstance(self._datas.get(key), dict) or isinstance(self._datas.get(key), OrderedDict):
                action_name = 'import_configurator_model_file'
                configurator_model_files = self._datas.get(key).get(action_name, {})
                if configurator_model_files:

                    self.logger.info("\t- %s : %s" % (key, action_name))
                    for configurator_model_file in configurator_model_files:
                        model_file = configurator_model_files[configurator_model_file]
                        model = model_file.get('model')
                        domain = model_file.get('domain')
                        order_by = model_file.get('order_by')
                        group_by = model_file.get('group_by')
                        load = model_file.get('load')
                        force_export_fields = model_file.get('force_export_fields', [])
                        excluded_fields = model_file.get('excluded_fields', [])
                        display_name_prefix_fields = model_file.get('display_name_prefix_fields', [])
                        file_name = model.replace('.', '_')
                        dest_path = os.path.dirname(self._configurator.paths[0]) + '/config'
                        res, files = self.get_configurator_records(model, domain,
                                                                   order_by=order_by,
                                                                   group_by=group_by,
                                                                   with_load=load,
                                                                   force_export_fields=force_export_fields,
                                                                   excluded_fields=excluded_fields,
                                                                   display_name_prefix_fields=display_name_prefix_fields)
                        open('%s/%s.yml' % (dest_path, file_name), 'w').write(res)

                # ##############################
                # #  CONFIGURATOR BINARY FILE  #
                # ##############################
                # action_name = 'import_configurator_binary_file'
                # configurator_model_files = self._datas.get(key).get(action_name, {})
                # if configurator_model_files:
                #     res = self.execute_odoo('ir.config_parameter', 'search_read',
                #                             [[('key', '=', 'odoo_configurator.access.token')],
                #                              ['value']],
                #                             {'context': self._context})
                #     if res:
                #         token = res[0].get('value', False)
                #     else:
                #         return
                #     url = '%s/teclib_configurator_generator/get_binary_file/%s' % \
                #           (self._configurator.connection._url, token)
                #     self.logger.info("\t- %s : %s" % (key, action_name))
                #     res = self.execute_odoo('ir.config_parameter', 'search_read',
                #                             [[('key', '=', 'odoo_configurator.access.token')],
                #                              ['value']],
                #                             {'context': self._context})
                #     if res:
                #         token = res[0].get('value', False)
                #         s = requests.Session()
                #         s.get(url='%s/web?db=%s' % (self._configurator.connection._url,
                #                                     self._configurator.connection._dbname))
                #
                #         for configurator_model_file in configurator_model_files:
                #             model_file = literal_eval(configurator_model_file)
                #             model = model_file[0]
                #             field = model_file[1]
                #             res_ids = model_file[2]
                #             for res_id in res_ids:
                #                 dest_path = os.path.dirname(self._configurator.paths[0]) + '/datas'
                #
                #                 r = s.get(url=url, params={'model': model, 'field': field, 'res_id': res_id})
                #
                #                 if r.headers['content-disposition']:
                #                     file_name = r.headers['content-disposition'].split('=')[1].split("''")[1]
                #                 else:
                #                     file_name = '%s_%s.bin' % (model.replace('.', '_'), res_id)
                #                 open('%s/%s' % (dest_path, file_name), 'wb').write(r.content)
