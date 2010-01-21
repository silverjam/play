<?xml version="1.0" ?>
<xsl:stylesheet 
	version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output
	method="text"
	/>	

<xsl:variable name="newline">
<xsl:text>
</xsl:text>
</xsl:variable>

<xsl:variable name="tab">
<xsl:text>	</xsl:text>
</xsl:variable>

<xsl:template name="tab-out">
	<xsl:param name="nodeset"/>
	<xsl:for-each select="$nodeset/ancestor::*">
		<xsl:value-of select="$tab" />
	</xsl:for-each>
</xsl:template>

<xsl:template match="node()">

	<xsl:if test="name(.) != ''" >

		<xsl:call-template name="tab-out">
			<xsl:with-param name="nodeset" select="." />
		</xsl:call-template>
	
		<xsl:text>&lt;</xsl:text>

		<xsl:value-of select="name(.)" />

		<xsl:if test="count(@*) != 0">		
			<xsl:value-of select="$newline" />
		</xsl:if>

		<xsl:apply-templates select="@*" />

		<xsl:choose>
			<xsl:when test="count(node()) != 0">
				<xsl:call-template name="tab-out">
					<xsl:with-param name="nodeset" select="@*" />
				</xsl:call-template>
				<xsl:text>&gt;</xsl:text>
			  <xsl:value-of select="$newline" />
			</xsl:when>

			<xsl:otherwise>

				<xsl:call-template name="tab-out">
					<xsl:with-param name="nodeset" select="." />
				</xsl:call-template>

				<xsl:text>/&gt;</xsl:text>
			  <xsl:value-of select="$newline" />

			</xsl:otherwise>
		</xsl:choose>

		<xsl:apply-templates select="node()">
			<xsl:sort select="@Name" />
		</xsl:apply-templates>

		<xsl:if test="count(node()) != 0">

				<xsl:call-template name="tab-out">
					<xsl:with-param name="nodeset" select="." />
				</xsl:call-template>

			<xsl:text>&lt;/</xsl:text>
			<xsl:value-of select="name(.)" />
			<xsl:text>&gt;</xsl:text>
			<xsl:value-of select="$newline" />
		</xsl:if>

	</xsl:if>

</xsl:template>

<xsl:template match="text()">
    <xsl:if test="normalize-space() != ''">
        <xsl:message terminate="yes">
            Non whitespace text data. VCProj files 
            should not have this!
        </xsl:message>
    </xsl:if>
</xsl:template>

<xsl:template name="entitize">
	<xsl:param name="s" />
	<xsl:if test="string-length($s) != 0">
		<xsl:variable name="c" select="substring($s, 1, 1)" />
		<xsl:choose>
			<xsl:when test="$c = '&#x0D;'">
				<xsl:text>&amp;#x0D;</xsl:text>
			</xsl:when>
			<xsl:when test="$c = '&#x0A;'">
				<xsl:text>&amp;#x0A;</xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$c" />
			</xsl:otherwise>
		</xsl:choose>
		<xsl:call-template name="entitize">
			<xsl:with-param name="s" select="substring($s, 2)" />
		</xsl:call-template>
	</xsl:if>
</xsl:template>

<xsl:template match="@*">

	<xsl:for-each select="ancestor::*">
    <xsl:value-of select="$tab" />
	</xsl:for-each>

	<xsl:value-of select="name(.)" />
	<xsl:text>="</xsl:text>

	<xsl:call-template name="entitize">
		<xsl:with-param name="s" select="." />
	</xsl:call-template>

	<xsl:text>"</xsl:text>

	<xsl:value-of select="$newline" />

</xsl:template>

</xsl:stylesheet>

<!-- vim: ts=2:sw=2:sts=2:noet:
-->
