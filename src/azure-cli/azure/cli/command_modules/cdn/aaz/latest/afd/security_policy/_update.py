# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# Code generated by aaz-dev-tools
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa

from azure.cli.core.aaz import *


@register_command(
    "afd security-policy update",
)
class Update(AAZCommand):
    """Update a new security policy within the specified profile.

    :example: Update the specified security policy's domain list.
        az afd security-policy update -g group --security-policy-name sp1 --profile-name profile --domains /subscriptions/sub1/resourcegroups/rg1/providers/Microsoft.Cdn/profiles/profile1/customDomains/customDomain1
    """

    _aaz_info = {
        "version": "2024-02-01",
        "resources": [
            ["mgmt-plane", "/subscriptions/{}/resourcegroups/{}/providers/microsoft.cdn/profiles/{}/securitypolicies/{}", "2024-02-01"],
        ]
    }

    AZ_SUPPORT_NO_WAIT = True

    AZ_SUPPORT_GENERIC_UPDATE = True

    def _handler(self, command_args):
        super()._handler(command_args)
        return self.build_lro_poller(self._execute_operations, self._output)

    _args_schema = None

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        if cls._args_schema is not None:
            return cls._args_schema
        cls._args_schema = super()._build_arguments_schema(*args, **kwargs)

        # define Arg Group ""

        _args_schema = cls._args_schema
        _args_schema.profile_name = AAZStrArg(
            options=["--profile-name"],
            help="Name of the Azure Front Door Standard or Azure Front Door Premium profile which is unique within the resource group.",
            required=True,
            id_part="name",
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
        )
        _args_schema.security_policy_name = AAZStrArg(
            options=["-n", "--name", "--security-policy-name"],
            help="Name of the security policy under the profile.",
            required=True,
            id_part="child_name_1",
        )

        # define Arg Group "Parameters"

        _args_schema = cls._args_schema
        _args_schema.web_application_firewall = AAZObjectArg(
            options=["--web-application-firewall"],
            arg_group="Parameters",
        )

        web_application_firewall = cls._args_schema.web_application_firewall
        web_application_firewall.associations = AAZListArg(
            options=["associations"],
            help="Waf associations",
            nullable=True,
        )
        web_application_firewall.waf_policy = AAZStrArg(
            options=["waf-policy"],
            help="The ID of Front Door WAF policy.",
            nullable=True,
        )

        associations = cls._args_schema.web_application_firewall.associations
        associations.Element = AAZObjectArg(
            nullable=True,
        )

        _element = cls._args_schema.web_application_firewall.associations.Element
        _element.domains = AAZListArg(
            options=["domains"],
            help="List of domains.",
            nullable=True,
        )
        _element.patterns_to_match = AAZListArg(
            options=["patterns-to-match"],
            help="List of paths",
            nullable=True,
        )

        domains = cls._args_schema.web_application_firewall.associations.Element.domains
        domains.Element = AAZObjectArg(
            nullable=True,
        )

        _element = cls._args_schema.web_application_firewall.associations.Element.domains.Element
        _element.id = AAZStrArg(
            options=["id"],
            help="Resource ID.",
            nullable=True,
        )

        patterns_to_match = cls._args_schema.web_application_firewall.associations.Element.patterns_to_match
        patterns_to_match.Element = AAZStrArg(
            nullable=True,
        )
        return cls._args_schema

    def _execute_operations(self):
        self.pre_operations()
        self.SecurityPoliciesGet(ctx=self.ctx)()
        self.pre_instance_update(self.ctx.vars.instance)
        self.InstanceUpdateByJson(ctx=self.ctx)()
        self.InstanceUpdateByGeneric(ctx=self.ctx)()
        self.post_instance_update(self.ctx.vars.instance)
        yield self.SecurityPoliciesCreate(ctx=self.ctx)()
        self.post_operations()

    @register_callback
    def pre_operations(self):
        pass

    @register_callback
    def post_operations(self):
        pass

    @register_callback
    def pre_instance_update(self, instance):
        pass

    @register_callback
    def post_instance_update(self, instance):
        pass

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return result

    class SecurityPoliciesGet(AAZHttpOperation):
        CLIENT_TYPE = "MgmtClient"

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [200]:
                return self.on_200(session)

            return self.on_error(session.http_response)

        @property
        def url(self):
            return self.client.format_url(
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Cdn/profiles/{profileName}/securityPolicies/{securityPolicyName}",
                **self.url_parameters
            )

        @property
        def method(self):
            return "GET"

        @property
        def error_format(self):
            return "MgmtErrorFormat"

        @property
        def url_parameters(self):
            parameters = {
                **self.serialize_url_param(
                    "profileName", self.ctx.args.profile_name,
                    required=True,
                ),
                **self.serialize_url_param(
                    "resourceGroupName", self.ctx.args.resource_group,
                    required=True,
                ),
                **self.serialize_url_param(
                    "securityPolicyName", self.ctx.args.security_policy_name,
                    required=True,
                ),
                **self.serialize_url_param(
                    "subscriptionId", self.ctx.subscription_id,
                    required=True,
                ),
            }
            return parameters

        @property
        def query_parameters(self):
            parameters = {
                **self.serialize_query_param(
                    "api-version", "2024-02-01",
                    required=True,
                ),
            }
            return parameters

        @property
        def header_parameters(self):
            parameters = {
                **self.serialize_header_param(
                    "Accept", "application/json",
                ),
            }
            return parameters

        def on_200(self, session):
            data = self.deserialize_http_content(session)
            self.ctx.set_var(
                "instance",
                data,
                schema_builder=self._build_schema_on_200
            )

        _schema_on_200 = None

        @classmethod
        def _build_schema_on_200(cls):
            if cls._schema_on_200 is not None:
                return cls._schema_on_200

            cls._schema_on_200 = AAZObjectType()
            _UpdateHelper._build_schema_security_policy_read(cls._schema_on_200)

            return cls._schema_on_200

    class SecurityPoliciesCreate(AAZHttpOperation):
        CLIENT_TYPE = "MgmtClient"

        def __call__(self, *args, **kwargs):
            request = self.make_request()
            session = self.client.send_request(request=request, stream=False, **kwargs)
            if session.http_response.status_code in [202]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200_201,
                    self.on_error,
                    lro_options={"final-state-via": "azure-async-operation"},
                    path_format_arguments=self.url_parameters,
                )
            if session.http_response.status_code in [200, 201]:
                return self.client.build_lro_polling(
                    self.ctx.args.no_wait,
                    session,
                    self.on_200_201,
                    self.on_error,
                    lro_options={"final-state-via": "azure-async-operation"},
                    path_format_arguments=self.url_parameters,
                )

            return self.on_error(session.http_response)

        @property
        def url(self):
            return self.client.format_url(
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Cdn/profiles/{profileName}/securityPolicies/{securityPolicyName}",
                **self.url_parameters
            )

        @property
        def method(self):
            return "PUT"

        @property
        def error_format(self):
            return "MgmtErrorFormat"

        @property
        def url_parameters(self):
            parameters = {
                **self.serialize_url_param(
                    "profileName", self.ctx.args.profile_name,
                    required=True,
                ),
                **self.serialize_url_param(
                    "resourceGroupName", self.ctx.args.resource_group,
                    required=True,
                ),
                **self.serialize_url_param(
                    "securityPolicyName", self.ctx.args.security_policy_name,
                    required=True,
                ),
                **self.serialize_url_param(
                    "subscriptionId", self.ctx.subscription_id,
                    required=True,
                ),
            }
            return parameters

        @property
        def query_parameters(self):
            parameters = {
                **self.serialize_query_param(
                    "api-version", "2024-02-01",
                    required=True,
                ),
            }
            return parameters

        @property
        def header_parameters(self):
            parameters = {
                **self.serialize_header_param(
                    "Content-Type", "application/json",
                ),
                **self.serialize_header_param(
                    "Accept", "application/json",
                ),
            }
            return parameters

        @property
        def content(self):
            _content_value, _builder = self.new_content_builder(
                self.ctx.args,
                value=self.ctx.vars.instance,
            )

            return self.serialize_content(_content_value)

        def on_200_201(self, session):
            data = self.deserialize_http_content(session)
            self.ctx.set_var(
                "instance",
                data,
                schema_builder=self._build_schema_on_200_201
            )

        _schema_on_200_201 = None

        @classmethod
        def _build_schema_on_200_201(cls):
            if cls._schema_on_200_201 is not None:
                return cls._schema_on_200_201

            cls._schema_on_200_201 = AAZObjectType()
            _UpdateHelper._build_schema_security_policy_read(cls._schema_on_200_201)

            return cls._schema_on_200_201

    class InstanceUpdateByJson(AAZJsonInstanceUpdateOperation):

        def __call__(self, *args, **kwargs):
            self._update_instance(self.ctx.vars.instance)

        def _update_instance(self, instance):
            _instance_value, _builder = self.new_content_builder(
                self.ctx.args,
                value=instance,
                typ=AAZObjectType
            )
            _builder.set_prop("properties", AAZObjectType, typ_kwargs={"flags": {"client_flatten": True}})

            properties = _builder.get(".properties")
            if properties is not None:
                properties.set_prop("parameters", AAZObjectType)

            parameters = _builder.get(".properties.parameters")
            if parameters is not None:
                parameters.set_const("type", "WebApplicationFirewall", AAZStrType, ".web_application_firewall", typ_kwargs={"flags": {"required": True}})
                parameters.discriminate_by("type", "WebApplicationFirewall")

            disc_web_application_firewall = _builder.get(".properties.parameters{type:WebApplicationFirewall}")
            if disc_web_application_firewall is not None:
                disc_web_application_firewall.set_prop("associations", AAZListType, ".web_application_firewall.associations")
                disc_web_application_firewall.set_prop("wafPolicy", AAZObjectType)

            associations = _builder.get(".properties.parameters{type:WebApplicationFirewall}.associations")
            if associations is not None:
                associations.set_elements(AAZObjectType, ".")

            _elements = _builder.get(".properties.parameters{type:WebApplicationFirewall}.associations[]")
            if _elements is not None:
                _elements.set_prop("domains", AAZListType, ".domains")
                _elements.set_prop("patternsToMatch", AAZListType, ".patterns_to_match")

            domains = _builder.get(".properties.parameters{type:WebApplicationFirewall}.associations[].domains")
            if domains is not None:
                domains.set_elements(AAZObjectType, ".")

            _elements = _builder.get(".properties.parameters{type:WebApplicationFirewall}.associations[].domains[]")
            if _elements is not None:
                _elements.set_prop("id", AAZStrType, ".id")

            patterns_to_match = _builder.get(".properties.parameters{type:WebApplicationFirewall}.associations[].patternsToMatch")
            if patterns_to_match is not None:
                patterns_to_match.set_elements(AAZStrType, ".")

            waf_policy = _builder.get(".properties.parameters{type:WebApplicationFirewall}.wafPolicy")
            if waf_policy is not None:
                waf_policy.set_prop("id", AAZStrType, ".web_application_firewall.waf_policy")

            return _instance_value

    class InstanceUpdateByGeneric(AAZGenericInstanceUpdateOperation):

        def __call__(self, *args, **kwargs):
            self._update_instance_by_generic(
                self.ctx.vars.instance,
                self.ctx.generic_update_args
            )


class _UpdateHelper:
    """Helper class for Update"""

    _schema_security_policy_read = None

    @classmethod
    def _build_schema_security_policy_read(cls, _schema):
        if cls._schema_security_policy_read is not None:
            _schema.id = cls._schema_security_policy_read.id
            _schema.name = cls._schema_security_policy_read.name
            _schema.properties = cls._schema_security_policy_read.properties
            _schema.system_data = cls._schema_security_policy_read.system_data
            _schema.type = cls._schema_security_policy_read.type
            return

        cls._schema_security_policy_read = _schema_security_policy_read = AAZObjectType()

        security_policy_read = _schema_security_policy_read
        security_policy_read.id = AAZStrType(
            flags={"read_only": True},
        )
        security_policy_read.name = AAZStrType(
            flags={"read_only": True},
        )
        security_policy_read.properties = AAZObjectType(
            flags={"client_flatten": True},
        )
        security_policy_read.system_data = AAZObjectType(
            serialized_name="systemData",
            flags={"read_only": True},
        )
        security_policy_read.type = AAZStrType(
            flags={"read_only": True},
        )

        properties = _schema_security_policy_read.properties
        properties.deployment_status = AAZStrType(
            serialized_name="deploymentStatus",
            flags={"read_only": True},
        )
        properties.parameters = AAZObjectType()
        properties.profile_name = AAZStrType(
            serialized_name="profileName",
            flags={"read_only": True},
        )
        properties.provisioning_state = AAZStrType(
            serialized_name="provisioningState",
            flags={"read_only": True},
        )

        parameters = _schema_security_policy_read.properties.parameters
        parameters.type = AAZStrType(
            flags={"required": True},
        )

        disc_web_application_firewall = _schema_security_policy_read.properties.parameters.discriminate_by("type", "WebApplicationFirewall")
        disc_web_application_firewall.associations = AAZListType()
        disc_web_application_firewall.waf_policy = AAZObjectType(
            serialized_name="wafPolicy",
        )

        associations = _schema_security_policy_read.properties.parameters.discriminate_by("type", "WebApplicationFirewall").associations
        associations.Element = AAZObjectType()

        _element = _schema_security_policy_read.properties.parameters.discriminate_by("type", "WebApplicationFirewall").associations.Element
        _element.domains = AAZListType()
        _element.patterns_to_match = AAZListType(
            serialized_name="patternsToMatch",
        )

        domains = _schema_security_policy_read.properties.parameters.discriminate_by("type", "WebApplicationFirewall").associations.Element.domains
        domains.Element = AAZObjectType()

        _element = _schema_security_policy_read.properties.parameters.discriminate_by("type", "WebApplicationFirewall").associations.Element.domains.Element
        _element.id = AAZStrType()
        _element.is_active = AAZBoolType(
            serialized_name="isActive",
            flags={"read_only": True},
        )

        patterns_to_match = _schema_security_policy_read.properties.parameters.discriminate_by("type", "WebApplicationFirewall").associations.Element.patterns_to_match
        patterns_to_match.Element = AAZStrType()

        waf_policy = _schema_security_policy_read.properties.parameters.discriminate_by("type", "WebApplicationFirewall").waf_policy
        waf_policy.id = AAZStrType()

        system_data = _schema_security_policy_read.system_data
        system_data.created_at = AAZStrType(
            serialized_name="createdAt",
        )
        system_data.created_by = AAZStrType(
            serialized_name="createdBy",
        )
        system_data.created_by_type = AAZStrType(
            serialized_name="createdByType",
        )
        system_data.last_modified_at = AAZStrType(
            serialized_name="lastModifiedAt",
        )
        system_data.last_modified_by = AAZStrType(
            serialized_name="lastModifiedBy",
        )
        system_data.last_modified_by_type = AAZStrType(
            serialized_name="lastModifiedByType",
        )

        _schema.id = cls._schema_security_policy_read.id
        _schema.name = cls._schema_security_policy_read.name
        _schema.properties = cls._schema_security_policy_read.properties
        _schema.system_data = cls._schema_security_policy_read.system_data
        _schema.type = cls._schema_security_policy_read.type


__all__ = ["Update"]
