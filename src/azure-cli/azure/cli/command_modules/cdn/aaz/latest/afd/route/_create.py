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
    "afd route create",
)
class Create(AAZCommand):
    """Create a new route with the specified route name under the specified subscription, resource group, profile, and AzureFrontDoor endpoint.

    :example: Creates a route to associate the endpoint's default domain with an origin group for all HTTPS requests.
        az afd route create -g group --endpoint-name endpoint1 --profile-name profile --route-name route1 --https-redirect Disabled --origin-group og001 --supported-protocols Https --link-to-default-domain Enabled --forwarding-protocol MatchRequest

    :example: Creates a route to associate the endpoint's default domain with an origin group for all requests and use the specified rule sets to customize the route behavior.
        az afd route create -g group --endpoint-name endpoint1 --profile-name profile --route-name route1 --rule-sets ruleset1 rulseset2 --origin-group og001 --supported-protocols Http Https --link-to-default-domain Enabled --forwarding-protocol MatchRequest --https-redirect Disabled

    :example: Creates a route to associate the endpoint's default domain and a custom domain with an origin group for all requests with the specified path patterns and redirect all trafic to use Https.
        az afd route create -g group --endpoint-name endpoint1 --profile-name profile --route-name route1 --patterns-to-match /test1/* /tes2/* --origin-group og001 --supported-protocols Http Https --custom-domains cd001 --forwarding-protocol MatchRequest --https-redirect Enabled --link-to-default-domain Enabled
    """

    _aaz_info = {
        "version": "2024-02-01",
        "resources": [
            ["mgmt-plane", "/subscriptions/{}/resourcegroups/{}/providers/microsoft.cdn/profiles/{}/afdendpoints/{}/routes/{}", "2024-02-01"],
        ]
    }

    AZ_SUPPORT_NO_WAIT = True

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
        _args_schema.endpoint_name = AAZStrArg(
            options=["--endpoint-name"],
            help="Name of the endpoint under the profile which is unique globally.",
            required=True,
        )
        _args_schema.profile_name = AAZStrArg(
            options=["--profile-name"],
            help="Name of the Azure Front Door Standard or Azure Front Door Premium profile which is unique within the resource group.",
            required=True,
        )
        _args_schema.resource_group = AAZResourceGroupNameArg(
            required=True,
        )
        _args_schema.route_name = AAZStrArg(
            options=["-n", "--name", "--route-name"],
            help="Name of the routing rule.",
            required=True,
        )

        # define Arg Group "OriginGroup"

        _args_schema = cls._args_schema
        _args_schema.origin_group = AAZStrArg(
            options=["--origin-group"],
            arg_group="OriginGroup",
            help="Name or ID of the origin group to be associated with.",
        )

        # define Arg Group "Properties"

        _args_schema = cls._args_schema
        _args_schema.cache_configuration = AAZObjectArg(
            options=["--cache-configuration"],
            arg_group="Properties",
            help="The caching configuration for this route. To disable caching, do not provide a cacheConfiguration object.",
        )
        _args_schema.formatted_custom_domains = AAZListArg(
            options=["--formatted-custom-domains"],
            arg_group="Properties",
            help="Domains referenced by this endpoint.",
        )
        _args_schema.enabled_state = AAZStrArg(
            options=["--enabled-state"],
            arg_group="Properties",
            help="Whether to enable use of this rule. Permitted values are 'Enabled' or 'Disabled'",
            enum={"Disabled": "Disabled", "Enabled": "Enabled"},
        )
        _args_schema.forwarding_protocol = AAZStrArg(
            options=["--forwarding-protocol"],
            arg_group="Properties",
            help="Protocol this rule will use when forwarding traffic to backends.",
            default="MatchRequest",
            enum={"HttpOnly": "HttpOnly", "HttpsOnly": "HttpsOnly", "MatchRequest": "MatchRequest"},
        )
        _args_schema.https_redirect = AAZStrArg(
            options=["--https-redirect"],
            arg_group="Properties",
            help="Whether to automatically redirect HTTP traffic to HTTPS traffic. Note that this is a easy way to set up this rule and it will be the first rule that gets executed.",
            default="Disabled",
            enum={"Disabled": "Disabled", "Enabled": "Enabled"},
        )
        _args_schema.link_to_default_domain = AAZStrArg(
            options=["--link-to-default-domain"],
            arg_group="Properties",
            help="whether this route will be linked to the default endpoint domain.",
            default="Disabled",
            enum={"Disabled": "Disabled", "Enabled": "Enabled"},
        )
        _args_schema.origin_path = AAZStrArg(
            options=["--origin-path"],
            arg_group="Properties",
            help="A directory path on the origin that AzureFrontDoor can use to retrieve content from, e.g. contoso.cloudapp.net/originpath.",
        )
        _args_schema.patterns_to_match = AAZListArg(
            options=["--patterns-to-match"],
            arg_group="Properties",
            help="The route patterns of the rule.",
        )
        _args_schema.formatted_rule_sets = AAZListArg(
            options=["--formatted-rule-sets"],
            arg_group="Properties",
            help="rule sets referenced by this endpoint.",
        )
        _args_schema.supported_protocols = AAZListArg(
            options=["--supported-protocols"],
            arg_group="Properties",
            help="List of supported protocols for this route.",
            default=["Http", "Https"],
        )

        cache_configuration = cls._args_schema.cache_configuration
        cache_configuration.compression_settings = AAZObjectArg(
            options=["compression-settings"],
            help="compression settings.",
        )
        cache_configuration.query_parameters = AAZStrArg(
            options=["query-parameters"],
            help="query parameters to include or exclude (comma separated).",
        )
        cache_configuration.query_string_caching_behavior = AAZStrArg(
            options=["query-string-caching-behavior"],
            help="Defines how Frontdoor caches requests that include query strings. You can ignore any query strings when caching, ignore specific query strings, cache every request with a unique URL, or cache specific query strings.",
            enum={"IgnoreQueryString": "IgnoreQueryString", "IgnoreSpecifiedQueryStrings": "IgnoreSpecifiedQueryStrings", "IncludeSpecifiedQueryStrings": "IncludeSpecifiedQueryStrings", "UseQueryString": "UseQueryString"},
        )

        compression_settings = cls._args_schema.cache_configuration.compression_settings
        compression_settings.content_types_to_compress = AAZListArg(
            options=["content-types-to-compress"],
            help="List of content types on which compression applies. The value should be a valid MIME type.",
        )
        compression_settings.is_compression_enabled = AAZBoolArg(
            options=["is-compression-enabled"],
            help="Indicates whether content compression is enabled on AzureFrontDoor. Default value is false. If compression is enabled, content will be served as compressed if user requests for a compressed version. Content won't be compressed on AzureFrontDoor when requested content is smaller than 1 byte or larger than 1 MB.",
        )

        content_types_to_compress = cls._args_schema.cache_configuration.compression_settings.content_types_to_compress
        content_types_to_compress.Element = AAZStrArg()

        formatted_custom_domains = cls._args_schema.formatted_custom_domains
        formatted_custom_domains.Element = AAZObjectArg()

        _element = cls._args_schema.formatted_custom_domains.Element
        _element.id = AAZStrArg(
            options=["id"],
            help="Resource ID.",
        )

        patterns_to_match = cls._args_schema.patterns_to_match
        patterns_to_match.Element = AAZStrArg()

        formatted_rule_sets = cls._args_schema.formatted_rule_sets
        formatted_rule_sets.Element = AAZObjectArg()
        cls._build_args_resource_reference_create(formatted_rule_sets.Element)

        supported_protocols = cls._args_schema.supported_protocols
        supported_protocols.Element = AAZStrArg(
            enum={"Http": "Http", "Https": "Https"},
        )
        return cls._args_schema

    _args_resource_reference_create = None

    @classmethod
    def _build_args_resource_reference_create(cls, _schema):
        if cls._args_resource_reference_create is not None:
            _schema.id = cls._args_resource_reference_create.id
            return

        cls._args_resource_reference_create = AAZObjectArg()

        resource_reference_create = cls._args_resource_reference_create
        resource_reference_create.id = AAZStrArg(
            options=["id"],
            help="Resource ID.",
        )

        _schema.id = cls._args_resource_reference_create.id

    def _execute_operations(self):
        self.pre_operations()
        yield self.RoutesCreate(ctx=self.ctx)()
        self.post_operations()

    @register_callback
    def pre_operations(self):
        pass

    @register_callback
    def post_operations(self):
        pass

    def _output(self, *args, **kwargs):
        result = self.deserialize_output(self.ctx.vars.instance, client_flatten=True)
        return result

    class RoutesCreate(AAZHttpOperation):
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
                "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Cdn/profiles/{profileName}/afdEndpoints/{endpointName}/routes/{routeName}",
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
                    "endpointName", self.ctx.args.endpoint_name,
                    required=True,
                ),
                **self.serialize_url_param(
                    "profileName", self.ctx.args.profile_name,
                    required=True,
                ),
                **self.serialize_url_param(
                    "resourceGroupName", self.ctx.args.resource_group,
                    required=True,
                ),
                **self.serialize_url_param(
                    "routeName", self.ctx.args.route_name,
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
                typ=AAZObjectType,
                typ_kwargs={"flags": {"required": True, "client_flatten": True}}
            )
            _builder.set_prop("properties", AAZObjectType, typ_kwargs={"flags": {"client_flatten": True}})

            properties = _builder.get(".properties")
            if properties is not None:
                properties.set_prop("cacheConfiguration", AAZObjectType, ".cache_configuration")
                properties.set_prop("customDomains", AAZListType, ".formatted_custom_domains")
                properties.set_prop("enabledState", AAZStrType, ".enabled_state")
                properties.set_prop("forwardingProtocol", AAZStrType, ".forwarding_protocol")
                properties.set_prop("httpsRedirect", AAZStrType, ".https_redirect")
                properties.set_prop("linkToDefaultDomain", AAZStrType, ".link_to_default_domain")
                properties.set_prop("originGroup", AAZObjectType, ".", typ_kwargs={"flags": {"required": True}})
                properties.set_prop("originPath", AAZStrType, ".origin_path")
                properties.set_prop("patternsToMatch", AAZListType, ".patterns_to_match")
                properties.set_prop("ruleSets", AAZListType, ".formatted_rule_sets")
                properties.set_prop("supportedProtocols", AAZListType, ".supported_protocols")

            cache_configuration = _builder.get(".properties.cacheConfiguration")
            if cache_configuration is not None:
                cache_configuration.set_prop("compressionSettings", AAZObjectType, ".compression_settings")
                cache_configuration.set_prop("queryParameters", AAZStrType, ".query_parameters")
                cache_configuration.set_prop("queryStringCachingBehavior", AAZStrType, ".query_string_caching_behavior")

            compression_settings = _builder.get(".properties.cacheConfiguration.compressionSettings")
            if compression_settings is not None:
                compression_settings.set_prop("contentTypesToCompress", AAZListType, ".content_types_to_compress")
                compression_settings.set_prop("isCompressionEnabled", AAZBoolType, ".is_compression_enabled")

            content_types_to_compress = _builder.get(".properties.cacheConfiguration.compressionSettings.contentTypesToCompress")
            if content_types_to_compress is not None:
                content_types_to_compress.set_elements(AAZStrType, ".")

            custom_domains = _builder.get(".properties.customDomains")
            if custom_domains is not None:
                custom_domains.set_elements(AAZObjectType, ".")

            _elements = _builder.get(".properties.customDomains[]")
            if _elements is not None:
                _elements.set_prop("id", AAZStrType, ".id")

            origin_group = _builder.get(".properties.originGroup")
            if origin_group is not None:
                origin_group.set_prop("id", AAZStrType, ".origin_group")

            patterns_to_match = _builder.get(".properties.patternsToMatch")
            if patterns_to_match is not None:
                patterns_to_match.set_elements(AAZStrType, ".")

            rule_sets = _builder.get(".properties.ruleSets")
            if rule_sets is not None:
                _CreateHelper._build_schema_resource_reference_create(rule_sets.set_elements(AAZObjectType, "."))

            supported_protocols = _builder.get(".properties.supportedProtocols")
            if supported_protocols is not None:
                supported_protocols.set_elements(AAZStrType, ".")

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
            _CreateHelper._build_schema_route_read(cls._schema_on_200_201)

            return cls._schema_on_200_201


class _CreateHelper:
    """Helper class for Create"""

    @classmethod
    def _build_schema_resource_reference_create(cls, _builder):
        if _builder is None:
            return
        _builder.set_prop("id", AAZStrType, ".id")

    _schema_resource_reference_read = None

    @classmethod
    def _build_schema_resource_reference_read(cls, _schema):
        if cls._schema_resource_reference_read is not None:
            _schema.id = cls._schema_resource_reference_read.id
            return

        cls._schema_resource_reference_read = _schema_resource_reference_read = AAZObjectType()

        resource_reference_read = _schema_resource_reference_read
        resource_reference_read.id = AAZStrType()

        _schema.id = cls._schema_resource_reference_read.id

    _schema_route_read = None

    @classmethod
    def _build_schema_route_read(cls, _schema):
        if cls._schema_route_read is not None:
            _schema.id = cls._schema_route_read.id
            _schema.name = cls._schema_route_read.name
            _schema.properties = cls._schema_route_read.properties
            _schema.system_data = cls._schema_route_read.system_data
            _schema.type = cls._schema_route_read.type
            return

        cls._schema_route_read = _schema_route_read = AAZObjectType()

        route_read = _schema_route_read
        route_read.id = AAZStrType(
            flags={"read_only": True},
        )
        route_read.name = AAZStrType(
            flags={"read_only": True},
        )
        route_read.properties = AAZObjectType(
            flags={"client_flatten": True},
        )
        route_read.system_data = AAZObjectType(
            serialized_name="systemData",
            flags={"read_only": True},
        )
        route_read.type = AAZStrType(
            flags={"read_only": True},
        )

        properties = _schema_route_read.properties
        properties.cache_configuration = AAZObjectType(
            serialized_name="cacheConfiguration",
        )
        properties.custom_domains = AAZListType(
            serialized_name="customDomains",
        )
        properties.deployment_status = AAZStrType(
            serialized_name="deploymentStatus",
            flags={"read_only": True},
        )
        properties.enabled_state = AAZStrType(
            serialized_name="enabledState",
        )
        properties.endpoint_name = AAZStrType(
            serialized_name="endpointName",
            flags={"read_only": True},
        )
        properties.forwarding_protocol = AAZStrType(
            serialized_name="forwardingProtocol",
        )
        properties.https_redirect = AAZStrType(
            serialized_name="httpsRedirect",
        )
        properties.link_to_default_domain = AAZStrType(
            serialized_name="linkToDefaultDomain",
        )
        properties.origin_group = AAZObjectType(
            serialized_name="originGroup",
            flags={"required": True},
        )
        cls._build_schema_resource_reference_read(properties.origin_group)
        properties.origin_path = AAZStrType(
            serialized_name="originPath",
        )
        properties.patterns_to_match = AAZListType(
            serialized_name="patternsToMatch",
        )
        properties.provisioning_state = AAZStrType(
            serialized_name="provisioningState",
            flags={"read_only": True},
        )
        properties.rule_sets = AAZListType(
            serialized_name="ruleSets",
        )
        properties.supported_protocols = AAZListType(
            serialized_name="supportedProtocols",
        )

        cache_configuration = _schema_route_read.properties.cache_configuration
        cache_configuration.compression_settings = AAZObjectType(
            serialized_name="compressionSettings",
        )
        cache_configuration.query_parameters = AAZStrType(
            serialized_name="queryParameters",
        )
        cache_configuration.query_string_caching_behavior = AAZStrType(
            serialized_name="queryStringCachingBehavior",
        )

        compression_settings = _schema_route_read.properties.cache_configuration.compression_settings
        compression_settings.content_types_to_compress = AAZListType(
            serialized_name="contentTypesToCompress",
        )
        compression_settings.is_compression_enabled = AAZBoolType(
            serialized_name="isCompressionEnabled",
        )

        content_types_to_compress = _schema_route_read.properties.cache_configuration.compression_settings.content_types_to_compress
        content_types_to_compress.Element = AAZStrType()

        custom_domains = _schema_route_read.properties.custom_domains
        custom_domains.Element = AAZObjectType()

        _element = _schema_route_read.properties.custom_domains.Element
        _element.id = AAZStrType()
        _element.is_active = AAZBoolType(
            serialized_name="isActive",
            flags={"read_only": True},
        )

        patterns_to_match = _schema_route_read.properties.patterns_to_match
        patterns_to_match.Element = AAZStrType()

        rule_sets = _schema_route_read.properties.rule_sets
        rule_sets.Element = AAZObjectType()
        cls._build_schema_resource_reference_read(rule_sets.Element)

        supported_protocols = _schema_route_read.properties.supported_protocols
        supported_protocols.Element = AAZStrType()

        system_data = _schema_route_read.system_data
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

        _schema.id = cls._schema_route_read.id
        _schema.name = cls._schema_route_read.name
        _schema.properties = cls._schema_route_read.properties
        _schema.system_data = cls._schema_route_read.system_data
        _schema.type = cls._schema_route_read.type


__all__ = ["Create"]
