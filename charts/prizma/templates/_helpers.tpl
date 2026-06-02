{{- define "prizma.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "prizma.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "prizma.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "prizma.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" -}}
{{- end -}}

{{- define "prizma.labels" -}}
helm.sh/chart: {{ include "prizma.chart" . }}
app.kubernetes.io/name: {{ include "prizma.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "prizma.selectorLabels" -}}
app.kubernetes.io/name: {{ include "prizma.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "prizma.componentLabels" -}}
app.kubernetes.io/component: {{ .component }}
{{- end -}}

{{- define "prizma.componentSelectorLabels" -}}
{{- $component := .component -}}
{{- $root := .root -}}
{{ include "prizma.selectorLabels" $root }}
app.kubernetes.io/component: {{ $component }}
{{- end -}}

{{- define "prizma.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "prizma.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{- define "prizma.secretName" -}}
{{- default (printf "%s-secrets" (include "prizma.fullname" .)) .Values.secrets.existingSecret -}}
{{- end -}}

{{- define "prizma.apiFullname" -}}
{{ include "prizma.fullname" . }}-api
{{- end -}}

{{- define "prizma.workerFullname" -}}
{{ include "prizma.fullname" . }}-worker
{{- end -}}

{{- define "prizma.minioFullname" -}}
{{ include "prizma.fullname" . }}-minio
{{- end -}}

{{- define "prizma.rabbitmqFullname" -}}
{{ include "prizma.fullname" . }}-rabbitmq
{{- end -}}

{{- define "prizma.tritonFullname" -}}
{{ include "prizma.fullname" . }}-triton
{{- end -}}
