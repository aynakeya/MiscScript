package mixsite

import "github.com/aynakeya/deepcolor"

var titleR = deepcolor.Item{
	Type: deepcolor.ItemTypeSingle,
	Rules: []deepcolor.ItemRule{
		{
			Selector: "dt.name",
			Target: deepcolor.TextTarget(),
			Substitution: map[string]string{
				"<span[^>]*>.*</span>":"",
			},
		},
	},
}

var tagsR = deepcolor.Item{
	Type:  deepcolor.ItemTypeList,
	Rules: []deepcolor.ItemRule{
		{
			Selector: "body > div.wrap > div.content.mb.clearfix > div.info > dl > dd:nth-child(4) > a",
			Target: deepcolor.TextTarget(),
		},
	},
}

var descR = deepcolor.Item{
	Type:  deepcolor.ItemTypeSingle,
	Rules: []deepcolor.ItemRule{
		{
			Selector: "div.des2",
			Target: deepcolor.TextTarget(),
			Substitution: map[string]string{
				"剧情：":"",
			},
		},
	},
}

var areayaerR = deepcolor.Item{
	Type:  deepcolor.ItemTypeSingle,
	Rules: []deepcolor.ItemRule{
		{
			Selector: "body > div.wrap > div.content.mb.clearfix > div.info > dl > dd:nth-child(3)",
			Target: deepcolor.TextTarget(),
			Substitution: map[string]string{
				"<b>地区：</b>":"",
				"(\\s)*<b>年代：</b>":"---",
			},
		},
	},
}

var areayaerR2 = deepcolor.Item{
	Type:  deepcolor.ItemTypeSingle,
	Rules: []deepcolor.ItemRule{
		{
			Selector: "body > div.wrap > div.content.mb.clearfix > div.info > dl > dd:nth-child(2)",
			Target: deepcolor.TextTarget(),
			Substitution: map[string]string{
				"<b>地区：</b>":"",
				"(\\s)*<b>年代：</b>":"---",
			},
		},
	},
}

var playid = deepcolor.Item{
	Type: deepcolor.ItemTypeSingle,
	Rules: []deepcolor.ItemRule{
		{
			Selector: "pl_id=[0-9]*;",
			Target: deepcolor.RegExpTarget(),
			Substitution: map[string]string{
				";":"",
				"pl_id=":"",
			},
		},
	},
}