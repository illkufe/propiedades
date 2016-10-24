from django.shortcuts import render
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView
from django.db.models import Sum
from django.http import JsonResponse
from xlrd import open_workbook
from datetime import datetime

from procesos.models import Propuesta, Factura
from utilidades.views import formato_numero
from locales.models import Local, Venta
from administrador.models import Cliente
from administrador.forms import ClienteForm, ClienteFormSet, Clasificacion_Detalle
from contrato.models import Contrato
from portal.forms import VentasForm

import json

modulo = 'Portal'
# Create your views here.

# ventas
class VentaList(ListView):
    model           = Venta
    template_name   = 'portal_cliente/ventas_list.html'

    def get_context_data(self, **kwargs):
        context = super(VentaList, self).get_context_data(**kwargs)
        context['title']        = modulo
        context['subtitle']     = 'ventas'
        context['name']         = 'lista'
        context['href']         = 'locales'
        context['form_venta']   = VentasForm(request=self.request)

        return context

class VENTAS(View):
    http_method_names = ['get', 'post', 'put', 'delete']

    def get(self, request, id=None):

        contrato	= Contrato.objects.filter(cliente_id=self.request.user.userprofile.cliente, visible=True).values_list('locales', flat=True)
        locales 	= Local.objects.filter(id__in=contrato, visible=True)

        if id == None:
            self.object_list = Venta.objects.filter(local_id__in=locales). \
                extra(select={'year': "EXTRACT(year FROM fecha_inicio)", 'month': "EXTRACT(month FROM fecha_inicio)",
                              'id': "id"}). \
                values('year', 'month', 'local_id'). \
                annotate(Sum('valor'))
        else:
            self.object_list = Venta.objects.filter(pk=id)

        if request.is_ajax():
            return self.json_to_response()

        if self.request.GET.get('format', None) == 'json':
            return self.json_to_response()

    def post(self, request):

        if self.request.POST.get('method') == 'delete':
            try:
                var_post        = request.POST.copy()
                local           = json.loads(var_post['venta'])
                nombre_local    = local['local']
                mes             = local['mes']
                ano             = local['ano']

                venta           = Venta.objects.get( local__nombre=nombre_local,
                                                     fecha_inicio__year=ano, fecha_termino__year=ano,
                                                     fecha_inicio__month=mes, fecha_termino__month=mes)
                venta.delete()


                estado = True
            except Exception as e:
                estado = False
            return JsonResponse({'estado': estado}, safe=False)
        else:

            tempfile    = request.FILES.get('file')

            book        = open_workbook(filename=None, file_contents=tempfile.read())
            sheet       = book.sheet_by_index(0)
            keys        = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
            title_excel = ['Codigo Local', 'Fecha Inicio', 'Fecha Termino', 'Total']

            errors  = list()
            estado  = 'ok'
            tipo    = ''

            if len(set(title_excel) & set(keys)) == 4:

                dict_list = []
                for row_index in range(1, sheet.nrows):
                    d = {keys[col_index]: sheet.cell(row_index, col_index).value for col_index in range(sheet.ncols)}
                    dict_list.append(d)
                cont = 1

                for i in dict_list:
                    list_error = list()

                    try:
                        list_error = self.validate_data(i['Fecha Inicio'], i['Fecha Termino'], i['Total'],
                                                        i['Codigo Local'])

                        if list_error:
                            estado  = 'error'
                            tipo    = 'data'

                            errors.append({
                                'row'		    : cont,
                                'local'			: i['Codigo Local'],'fecha_inicio'	: i['Fecha Inicio'],
                                'fecha_termino'	: i['Fecha Termino'],
                                'valor'			: i['Total'],
                                'error'			: list_error
                            })

                    except ValueError as a:
                        estado 	= 'error'
                        tipo 	= 'data'

                        errors.append({
                            'row'			: cont,
                            'local'			: i['Codigo Local'],
                            'fecha_inicio'	: i['Fecha Inicio'],
                            'fecha_termino'	: i['Fecha Termino'],
                            'valor'			: i['Total'],
                            'error'			: list_error
                        })
                    cont +=1
            else:
                estado = 'error'
                tipo   = 'formato'
                errors.append({
                    'error'			: 'Formato de Excel subido es incorrecto.'
                })


            if not errors:
                for i in dict_list:
                    fecha_inicio 	= datetime.strptime(i[ 'Fecha Inicio'], '%d-%m-%Y')
                    fecha_termino 	= datetime.strptime(i[ 'Fecha Termino'], '%d-%m-%Y')
                    valor 			= i['Total']
                    local 			= i['Codigo Local']

                    if Venta.objects.filter(fecha_inicio=fecha_inicio, fecha_termino=fecha_termino,
                                            local__codigo=local).exists():

                        venta = Venta.objects.get(fecha_inicio=fecha_inicio, fecha_termino=fecha_termino,
                                                  local__codigo=local)
                        venta.valor = valor
                        venta.save()

                    else:
                        venta = Venta(
                            fecha_inicio	= fecha_inicio,
                            fecha_termino	= fecha_termino,
                            valor			= valor,
                            local_id 		= Local.objects.get(codigo=local).id,
                            periodicidad	= 3,
                        )
                        venta.save()

            if self.request.is_ajax():
                data = {
                    'estado': estado,
                    'tipo'	: tipo,
                    'errors': errors,
                }
                return JsonResponse(data)
            else:
                return render(request, 'portal_cliente/ventas_list.html')

    def validate_data(self, fecha_inicio, fecha_termino, valor, local):

        list_error = list()

        fechas =[ fecha_inicio,
            fecha_termino
        ]

        contrato	= Contrato.objects.filter(cliente_id=self.request.user.userprofile.cliente, visible=True).values_list('locales', flat=True)
        locales 	= Local.objects.filter(id__in=contrato, codigo=local, visible=True).exists()

        error_fecha = False

        try:
            float(valor)
        except Exception:
            error = "Valor no válido."
            list_error.append(error)


        if not locales:
            error = "Local no pertenece a empresa."
            list_error.append(error)

        for a in fechas:
            try:
                datetime.strptime(a, '%d-%m-%Y')
            except Exception as e:

                error 		= "Formato fecha no válido."
                error_fecha = True

                if not error in list_error:
                    list_error.append(error)

        if not error_fecha:
            if datetime.strptime(fechas[1], '%d-%m-%Y') < datetime.strptime(fechas[0], '%d-%m-%Y'):
                error = "Fecha Termino no puede ser menor a fecha Inicio."
                list_error.append(error)

        return list_error

    def delete(self, request):

        try:
            venta 		= Venta.objects.get(pk=id)
            venta.delete()

            estado = True
        except Exception:
            estado = False
        return JsonResponse({'estado': estado}, safe=False)

    def json_to_response(self):

        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        data = list()

        for venta in self.object_list:

            local = Local.objects.get(id=int(venta['local_id']))

            data.append({
                'id'			: 1,
                'local_id'		: local.id,
                'local_nombre'	: local.nombre,
                'nro_mes'		: int(venta['month']),
                'mes'			: meses[int(venta['month'])-1],
                'ano'			: venta['year'],
                'valor'			: formato_numero(venta['valor__sum']),
            })

        return JsonResponse(data, safe=False)


class VentaDiaria(View):
    http_method_names = ['post']

    def post(self, request):
        try:
            form_venta = VentasForm(self.request.POST, request=self.request)
            if form_venta.is_valid():
                data    = form_venta.cleaned_data
                fecha   = data.get('fecha_inicio')
                local   = data.get('local')
                valor   = data.get('valor')

                if Venta.objects.filter(fecha_inicio=fecha, fecha_termino=fecha, local=local).exists():

                    update_venta = Venta.objects.get(fecha_inicio=fecha, fecha_termino=fecha, local=local)
                    update_venta.valor = valor
                    update_venta.save()


                else:
                    new_venta               = Venta()
                    new_venta.local         = local
                    new_venta.fecha_inicio  = fecha
                    new_venta.fecha_termino = fecha
                    new_venta.valor         = valor
                    new_venta.periodicidad  = 3
                    new_venta.save()
            else:
                return JsonResponse(form_venta.errors, status=400)
            estado = True
        except Exception as d:
            error = d
            estado = False

        return JsonResponse({'estado': estado}, safe=False)


# cliente
class ClienteMixin(object):

    template_name 	= 'portal_cliente/cliente_visualize.html'
    form_class 		= ClienteForm
    success_url 	= '/clientes/list'

    def form_invalid(self, form):

        response = super(ClienteMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):

        context 			= self.get_context_data()
        form_representante 	= context['representante_form']

        obj 		= form.save(commit=False)
        obj.empresa = self.request.user.userprofile.empresa
        obj.save()
        form.save_m2m()



        if form_representante.is_valid():
            self.object 				= form.save(commit=False)
            form_representante.instance = self.object
            form_representante.save()

        response = super(ClienteMixin, self).form_valid(form)

        if self.request.is_ajax():
            data = {'estado' : True,}
            return JsonResponse(data)
        else:
            return response

class ClienteUpdatePortal(ClienteMixin, UpdateView):

	model 			= Cliente
	form_class 		= ClienteForm
	template_name 	= 'portal_cliente/cliente_visualize.html'
	success_url 	= '/'

	def get_context_data(self, **kwargs):

		context 					= super(ClienteUpdatePortal, self).get_context_data(**kwargs)
		context['title'] 			= 'Datos Generales'
		context['subtitle'] 		= 'cliente'
		context['name'] 			= 'editar'
		context['href'] 			= ''
		context['accion'] 			= 'update'

		cliente_id  				= self.kwargs.pop('pk', None)
		data        				= obtener_clasificacion(self, cliente_id)
		context['clasificaciones'] 	= data
		context['facturas']			= facturas_generadas(self)


		if self.request.POST:
			context['representante_form'] = ClienteFormSet(self.request.POST, instance=self.object)
		else:
			context['representante_form'] = ClienteFormSet(instance=self.object)

		return context

def obtener_clasificacion(self, cliente_id):
    cabeceras   = self.request.user.userprofile.empresa.clasificacion_set.filter(visible=True, tipo_clasificacion=2)
    cabecera    = list()

    if cliente_id is None:

        for c in cabeceras:

            detalles    = Clasificacion_Detalle.objects.filter(clasificacion=c)
            detalle     = list()

            for d in detalles:
                detalle.append({
                    'id'    : d.id,
                    'nombre': d.nombre,
                    'select': False
                })

            cabecera.append({
                'id'        : c.id,
                'nombre'    : c.nombre,
                'detalle'   : detalle
            })
    else:
        for c in cabeceras:

            detalles    = Clasificacion_Detalle.objects.filter(clasificacion=c)
            detalle     = list()

            for d in detalles:
                detalle.append({
                    'id'    : d.id,
                    'nombre': d.nombre,
                    'select': False if not d.cliente_set.filter(id=cliente_id).exists() else True
                })

            cabecera.append({
                'id'        : c.id,
                'nombre'    : c.nombre,
                'detalle'   : detalle
            })

    return cabecera

def facturas_generadas(self):
	contratos_cliente = self.request.user.userprofile.cliente.contrato_set.values_list('id', flat=True)
	try:
		facturas = Factura.objects.filter(contrato_id__in=contratos_cliente, estado_id=2).__bool__()
	except Exception:
		facturas = False

	return facturas


#Facturas
class PropuestaProcesarPortalClienteList(ListView):
	model           = Propuesta
	template_name   = 'portal_cliente/propuesta_procesar_list.html'

	def get_context_data(self, **kwargs):

		users       = self.request.user.userprofile.cliente.empresa.userprofile_set.all().values_list('user_id', flat=True)
		propuestas  = Propuesta.objects.filter(user__in=users).values_list('id', flat=True)

		context = super(PropuestaProcesarPortalClienteList, self).get_context_data(**kwargs)
		context['title']    = 'Facturas / Pedidos'
		context['subtitle'] = 'propuestas de facturación'
		context['name']     = 'lista'
		context['href']     = '/'

		context['facturas_procesadas'] = Factura.objects.filter(propuesta__in=propuestas,
                                                                estado_id__in=[2, 4, 5],
																visible=True)

		return context
