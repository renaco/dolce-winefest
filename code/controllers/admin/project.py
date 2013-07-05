import logging

from tornado.web import HTTPError, authenticated
from mongoengine.queryset import OperationError

from controllers import RequestHandler, ListMixin
from models import Ubigeo, Project, Contact, Specs, Characteristics, Image
from forms import ProjectForm, ContactAdminForm, SpecsForm, CharacteristicsForm


class AddOrEdit(RequestHandler):

    def initialize(self, externo=False):
        self.externo = externo

    @authenticated
    def get(self, project_id=None, status_code=None, **kwargs):

        project = None
        provinces = None
        districts = None

        if project_id:
            project = Project.objects.with_id(project_id)
            if not project:
                raise HTTPError(404)

            if 'project_form' not in kwargs:
                kwargs['project_form'] = ProjectForm(obj=project)
                kwargs['contact_form'] = ContactAdminForm(obj=project.contact)
                kwargs['specs_form'] = SpecsForm(obj=project.specs)
                kwargs['characteristics_form'] = CharacteristicsForm(
                    obj=project.characteristics)

            provinces = Ubigeo.objects(
                department_code=project.ubigeo.department_code,
                province_code__ne='00',
                district_code='00'
            ).only('name', 'province_code').order_by('name')

            districts = Ubigeo.objects(
                department_code=project.ubigeo.department_code,
                province_code=project.ubigeo.province_code,
                district_code__ne='00'
            ).only('name', 'district_code').order_by('name')
        else:
            if 'project_form' not in kwargs:
                kwargs['project_form'] = ProjectForm()
                kwargs['contact_form'] = ContactAdminForm()
                kwargs['specs_form'] = SpecsForm()
                kwargs['characteristics_form'] = CharacteristicsForm()

        self.render(
            'admin/projects/%s.html' % (
                'create' if not project_id else 'edit'),
            externo=self.externo if not project_id else project.externo,
            data=project,
            status_code=status_code,
            types=Project.TYPES,
            departments=Ubigeo.objects(
                district_code='00',
                province_code='00',
            ).only('name', 'department_code').order_by('name'),
            provinces=provinces,
            districts=districts,
            **kwargs
        )

    @authenticated
    def post(self, project_id=None):
        project = None
        if project_id:
            project = Project.objects.with_id(project_id)
            if not project:
                raise HTTPError(404)

        status_code = None
        project_form = ProjectForm(self.request_data)
        contact_form = ContactAdminForm(self.request_data, prefix='contact_')
        specs_form = SpecsForm(self.request_data, prefix='specs_')
        characteristics_form = CharacteristicsForm(
                self.request_data, prefix='chars_')

        if project_form.validate() and contact_form.validate() and \
            specs_form.validate() and characteristics_form.validate():

            contact = Contact(
                name=contact_form.name.data,
                email=contact_form.email.data,
                phone=contact_form.phone.data,
                address=contact_form.address.data,
            )

            specs = Specs(
                builder=specs_form.builder.data,
                num_available=specs_form.num_available.data,
                floor=specs_form.floor.data,
                area_min=specs_form.area_min.data,
                area_max=specs_form.area_max.data,
                price_min=specs_form.price_min.data,
                price_max=specs_form.price_max.data,
                web=specs_form.web.data,
            )

            characteristics = Characteristics(
                serviceroom=characteristics_form.serviceroom.data,
                gas=characteristics_form.gas.data,
                swimming_pool=characteristics_form.swimming_pool.data,
                closet=characteristics_form.closet.data,
                laundry=characteristics_form.laundry.data,
                park_view=characteristics_form.park_view.data,
                terrace=characteristics_form.terrace.data,
                garden=characteristics_form.garden.data,
                furnished=characteristics_form.furnished.data,
                kitchen_cabinet=characteristics_form.kitchen_cabinet.data,
            )

            project = project or Project()
            project.title = project_form.title.data
            project.price = project_form.price.data
            project.address = project_form.address.data
            project.description = project_form.description.data
            project.specs = specs
            project.characteristics = characteristics
            project.contact = contact
            project.status = project_form.status.data
            project.type = project_form.type.data
            project.bedrooms = project_form.bedrooms.data
            project.bathrooms = project_form.bathrooms.data
            project.garages = project_form.garages.data
            project.ubigeo = Ubigeo.objects.with_id(project_form.ubigeo.data)
            project.externo = project_form.externo.data

            if project_id and 'imagen' in self.request.files:
                has_images = len(project.images)
                images = []

                for imgfile in self.request.files['imagen']:
                    try:
                        img = Image()
                        img.save(raw_data=imgfile['body'])
                    except Exception as exc:
                        logging.warning(exc)
                    else:
                        images.append(img)

                if images:
                    if not has_images:
                        project.images = images
                        project.selected_image = images[0]
                    else:
                        project.images.extend(images)

            if self.get_argument('image_selected', ''):
                project.selected_image = Image.objects\
                        .with_id(self.get_argument('image_selected'))

            try:
                project.save()
                status_code = 0
            except OperationError as exc:
                logging.error(exc)
                status_code = 1
            except Exception as exc:
                logging.error(exc)
                #status_code |= 2
            else:
                if not project_id:
                    self.redirect(
                        self.reverse_url('admin_project_edit', project.id))
                    return

        logging.error(project_form.errors)
        logging.error(contact_form.errors)
        logging.error(specs_form.errors)
        logging.error(characteristics_form.errors)

        self.get(
            project_id=project_id,
            status_code=status_code,
            project_form=project_form,
            contact_form=contact_form,
            specs_form=specs_form,
            characteristics_form=characteristics_form
        )


class Delete(RequestHandler):

    @authenticated
    def post(self):
        if self.request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            raise HTTPError(403)

        status_code = 0

        try:
            project = Project.objects.with_id(self.get_argument('project_id'))
        except Exception as exc:
            logging.error(exc)
            raise HTTPError(404)

        try:
            project.delete()
        except OperationError as exc:
            logging.error(exc)
            status_code |= 1
        except Exception as exc:
            logging.error(exc)
            status_code |= 2

        self.finish({'status_code': status_code})


class List(RequestHandler, ListMixin):

    def initialize(self, externo=False):
        self.externo = externo

    @authenticated
    def get(self):
        filters = {'externo' + ('' if self.externo else '__ne'): True}

        queryset = Project.objects.only('title', 'status')\
                .filter(**filters)\
                .order_by('-created_at', '-updated_at')

        self.render(
            'admin/projects/list.html',
            externo=self.externo,
            **self.get_pagination(count=queryset.count(), query=queryset)
        )


class DeleteImage(RequestHandler):

    @authenticated
    def post(self):
        if self.request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            raise HTTPError(403)

        status_code = 0
        image = Image.objects.with_id(self.get_argument('image_id'))
        project = Project.objects.with_id(self.get_argument('project_id'))

        if not image:
            raise HTTPError(404)

        try:
            image.delete(project=project)
        except OperationError as exc:
            logging.error(exc)
            status_code |= 1
        except Exception as exc:
            logging.error(exc)
            pass

        self.finish({'status_code': status_code})
